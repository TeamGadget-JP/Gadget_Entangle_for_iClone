using UnityEngine;
using System;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.IO;
using System.Text;
using System.Collections.Generic;

#if UNITY_EDITOR
using UnityEditor;
#endif

namespace Gadget.GEi
{
    [ExecuteAlways]
    public class GEi_Receiver : MonoBehaviour
    {
        [Header("Network Configuration")]
        public int listenPort = 8990;
        public bool isListening = false;
        public bool runInBackground = true; 

        [Header("Target Architecture")]
        public GameObject targetCharacter;
        
        [Header("Smoothing (Interpolation)")]
        public bool useLerp = true; 
        [Range(1f, 100f)] public float rootLerpSpeed = 60f;
        [Range(1f, 100f)] public float bodyLerpSpeed = 60f;
        [Range(1f, 100f)] public float fingerLerpSpeed = 60f;

        [Header("World Space Tuning (Avatar Root)")]
        public bool rootSwapYZ = true; 
        public Vector3 rootPosMultiplier = new Vector3(1f, 1f, 1f);
        [Tooltip("Default W is -1 for Right-Handed to Left-Handed conversion")]
        public Vector4 rootRotMultiplier = new Vector4(1f, 1f, 1f, -1f); 
        public Vector3 rootPosOffset = Vector3.zero;
        public Vector3 rootRotOffset = Vector3.zero; 

        [Header("Local Bone Tuning")]
        public float positionScale = 0.01f; 
        public Vector3 posMultiplier = new Vector3(-1f, 1f, 1f);
        public Vector4 rotMultiplier = new Vector4(-1f, 1f, 1f, -1f);

        [Header("Eye Bone Specific Tuning")]
        public bool enableEyeTuning = false;
        public bool swapEyeXZ = true; 
        public Vector4 eyeRotMultiplier = new Vector4(1f, 1f, 1f, 1f);

        [Header("Facial Morph (Blendshape) Tuning")]
        public float morphMultiplier = 100f;

        [Header("Hybrid Synchronization (Co-op Mode)")]
        [Tooltip("Disable this if another system (e.g., GEC) is driving the Avatar Root position.")]
        public bool applyRootTransform = false; 

        private UdpClient udpClient;
        private Thread receiveThread;
        private byte[] pendingBytes = null;
        private bool hasNewData = false;
        private readonly object lockObj = new object();

        private Dictionary<string, Transform> boneMap = new Dictionary<string, Transform>();
        private Dictionary<string, Vector3> targetPos = new Dictionary<string, Vector3>();
        private Dictionary<string, Quaternion> targetRot = new Dictionary<string, Quaternion>();
        private Dictionary<string, float> targetMorphs = new Dictionary<string, float>();
        private HashSet<string> activeBones = new HashSet<string>();
        
        private Vector3 rootTargetPos;
        private Quaternion rootTargetRot;
        
        private SkinnedMeshRenderer[] cachedSMRs;

        private void OnEnable() 
        { 
            if (isListening) StartListening(); 
#if UNITY_EDITOR
            EditorApplication.update += EditorUpdate; 
#endif
        }

        private void OnDisable() 
        { 
            StopListening(); 
#if UNITY_EDITOR
            EditorApplication.update -= EditorUpdate; 
#endif
        }

        private void Start() 
        { 
            if (Application.isPlaying && runInBackground) 
            { 
                Application.runInBackground = true; 
                Application.targetFrameRate = 60; 
            }
            EnsureBonesBound(); 
        }

        private void EnsureBonesBound() 
        { 
            if (targetCharacter != null && boneMap.Count == 0) BindBones(); 
        }

        private void BindBones()
        {
            boneMap.Clear(); targetPos.Clear(); targetRot.Clear(); targetMorphs.Clear(); activeBones.Clear();
            Transform[] allBones = targetCharacter.GetComponentsInChildren<Transform>();
            foreach (Transform t in allBones)
            {
                boneMap[t.name] = t;
                targetPos[t.name] = t.localPosition; 
                targetRot[t.name] = t.localRotation;
            }
            if (targetCharacter != null) 
            {
                rootTargetPos = targetCharacter.transform.position;
                rootTargetRot = targetCharacter.transform.rotation;
                cachedSMRs = targetCharacter.GetComponentsInChildren<SkinnedMeshRenderer>();
            }
        }

        private void LateUpdate() 
        { 
            if (Application.isPlaying) 
            { 
                EnsureBonesBound(); 
                HandleUDP(); 
                ApplyTransforms(); 
            } 
        }

#if UNITY_EDITOR
        private void EditorUpdate() 
        { 
            if (!Application.isPlaying) 
            { 
                EnsureBonesBound(); 
                HandleUDP(); 
                ApplyTransforms(); 

                if (isListening) 
                {
                    UnityEditorInternal.InternalEditorUtility.RepaintAllViews();
                }
            } 
        }
#endif

        private void HandleUDP()
        {
            if (isListening && udpClient == null) StartListening();
            else if (!isListening && udpClient != null) StopListening();

            byte[] dataToProcess = null;
            bool shouldProcess = false;

            lock (lockObj) 
            { 
                if (hasNewData && isListening) 
                { 
                    dataToProcess = pendingBytes; 
                    hasNewData = false; 
                    shouldProcess = true; 
                } 
            }
            if (shouldProcess && dataToProcess != null) ProcessBinary(dataToProcess);
        }

        private void StartListening()
        {
            if (udpClient != null) return;
            try 
            { 
                udpClient = new UdpClient(listenPort); 
                receiveThread = new Thread(ReceiveLoop) { IsBackground = true }; 
                receiveThread.Start(); 
            } 
            catch 
            { 
                StopListening(); 
            }
        }

        private void ReceiveLoop()
        {
            IPEndPoint ep = new IPEndPoint(IPAddress.Any, 0);
            while (isListening && udpClient != null)
            {
                try 
                { 
                    byte[] buffer = udpClient.Receive(ref ep); 
                    lock (lockObj) 
                    { 
                        pendingBytes = buffer; 
                        hasNewData = true; 
                    } 
                } 
                catch { }
            }
        }

        private void StopListening() 
        { 
            isListening = false; 
            if (udpClient != null) 
            { 
                udpClient.Close(); 
                udpClient = null; 
            } 
            receiveThread = null; 
        }

        private void ProcessBinary(byte[] data)
        {
            try 
            {
                using (MemoryStream ms = new MemoryStream(data))
                using (BinaryReader br = new BinaryReader(ms, Encoding.UTF8))
                {
                    if (br.ReadByte() != 'G' || br.ReadByte() != 'I' || br.ReadByte() != 'C' || br.ReadByte() != 'B') return;
                    
                    br.ReadByte(); 
                    int charIdLen = br.ReadByte();
                    br.ReadBytes(charIdLen); 

                    float rtx = br.ReadSingle(), rty = br.ReadSingle(), rtz = br.ReadSingle();
                    float rrx = br.ReadSingle(), rry = br.ReadSingle(), rrz = br.ReadSingle(), rrw = br.ReadSingle();
                    
                    if (rootSwapYZ)
                    {
                        rootTargetPos = new Vector3(rtx * rootPosMultiplier.x, rtz * rootPosMultiplier.y, rty * rootPosMultiplier.z) * positionScale + rootPosOffset;
                        rootTargetRot = new Quaternion(rrx * rootRotMultiplier.x, rrz * rootRotMultiplier.y, rry * rootRotMultiplier.z, rrw * rootRotMultiplier.w) * Quaternion.Euler(rootRotOffset);
                    }
                    else
                    {
                        rootTargetPos = new Vector3(rtx * rootPosMultiplier.x, rty * rootPosMultiplier.y, rtz * rootPosMultiplier.z) * positionScale + rootPosOffset;
                        rootTargetRot = new Quaternion(rrx * rootRotMultiplier.x, rry * rootRotMultiplier.y, rrz * rootRotMultiplier.z, rrw * rootRotMultiplier.w) * Quaternion.Euler(rootRotOffset);
                    }

                    int numBones = br.ReadByte();
                    HashSet<string> incomingBones = new HashSet<string>();

                    for (int i = 0; i < numBones; i++)
                    {
                        int nameLen = br.ReadByte();
                        string boneName = Encoding.UTF8.GetString(br.ReadBytes(nameLen));
                        br.ReadByte(); 
                        
                        incomingBones.Add(boneName); 

                        float tx = br.ReadSingle(), ty = br.ReadSingle(), tz = br.ReadSingle();
                        float rx = br.ReadSingle(), ry = br.ReadSingle(), rz = br.ReadSingle(), rw = br.ReadSingle();

                        if (targetPos.ContainsKey(boneName))
                        {
                            targetPos[boneName] = new Vector3(tx * posMultiplier.x, ty * posMultiplier.y, tz * posMultiplier.z) * positionScale;

                            if (enableEyeTuning && boneName.Contains("Eye"))
                            {
                                if (swapEyeXZ) { float temp = rx; rx = rz; rz = temp; }
                                targetRot[boneName] = new Quaternion(rx * eyeRotMultiplier.x, ry * eyeRotMultiplier.y, rz * eyeRotMultiplier.z, rw * eyeRotMultiplier.w);
                            }
                            else
                            {
                                targetRot[boneName] = new Quaternion(rx * rotMultiplier.x, ry * rotMultiplier.y, rz * rotMultiplier.z, rw * rotMultiplier.w);
                            }
                        }
                    }
                    
                    activeBones = incomingBones;

                    if (ms.Position < ms.Length)
                    {
                        int numMorphs = br.ReadByte(); 
                        HashSet<string> currentPacketMorphs = new HashSet<string>();

                        for (int i = 0; i < numMorphs; i++)
                        {
                            int mNameLen = br.ReadByte();
                            string morphName = Encoding.UTF8.GetString(br.ReadBytes(mNameLen));
                            float morphWeight = br.ReadSingle(); 
                            targetMorphs[morphName] = morphWeight;
                            currentPacketMorphs.Add(morphName); 
                        }

                        List<string> keysToZero = new List<string>();
                        foreach (var key in targetMorphs.Keys)
                        {
                            if (!currentPacketMorphs.Contains(key)) 
                            {
                                keysToZero.Add(key);
                            }
                        }
                        foreach (var key in keysToZero)
                        {
                            targetMorphs[key] = 0f; 
                        }
                    }

                    if (cachedSMRs != null) 
                    {
                        foreach (var smr in cachedSMRs) 
                        { 
                            if(smr != null)
                            { 
                                smr.updateWhenOffscreen = true;
                                
#if UNITY_EDITOR
                                if (!Application.isPlaying) 
                                { 
                                    smr.localBounds = smr.localBounds;
                                    smr.transform.hasChanged = true;
                                    EditorUtility.SetDirty(smr);
                                }
#endif
                            } 
                        }
                    }
                }
            } 
            catch { }
        }

        private void ApplyTransforms()
        {
            if (targetCharacter == null) return;

            if (applyRootTransform)
            {
                float rt = useLerp ? (rootLerpSpeed / 60f) : 1f;
                targetCharacter.transform.position = Vector3.Lerp(targetCharacter.transform.position, rootTargetPos, rt);
                targetCharacter.transform.rotation = Quaternion.Slerp(targetCharacter.transform.rotation, rootTargetRot, rt);
            }

            foreach (var kvp in boneMap)
            {
                string name = kvp.Key;
                Transform bone = kvp.Value;
                if (bone == null || name == targetCharacter.name) continue;

                if (!activeBones.Contains(name)) continue;

                bool isExtremity = name.Contains("Index") || name.Contains("Mid") || name.Contains("Pinky") || name.Contains("Ring") || name.Contains("Thumb") || name.Contains("Toe") || name.Contains("Eye");
                float currentLerpSpeed = isExtremity ? fingerLerpSpeed : bodyLerpSpeed;
                float t = useLerp ? (currentLerpSpeed / 60f) : 1f; 
                
                if (name.Contains("Root") || name.Contains("Hip") || name.Contains("Pelvis") || name.Contains("Waist") || name.Contains("Spine") || name.Contains("Head") || name.Contains("Jaw"))
                {
                    bone.localPosition = Vector3.Lerp(bone.localPosition, targetPos[name], t);
                }
                
                bone.localRotation = Quaternion.Slerp(bone.localRotation, targetRot[name], t);
            }

#if UNITY_EDITOR
            if (!Application.isPlaying && cachedSMRs != null)
            {
                foreach (var smr in cachedSMRs)
                {
                    if (smr != null)
                    {
                        smr.enabled = false;
                        smr.enabled = true;
                    }
                }
            }
#endif

            if (cachedSMRs != null && targetMorphs.Count > 0)
            {
                foreach (var smr in cachedSMRs)
                {
                    if (smr == null || smr.sharedMesh == null) continue;
                    foreach (var morph in targetMorphs)
                    {
                        int blendShapeIndex = smr.sharedMesh.GetBlendShapeIndex(morph.Key);
                        if (blendShapeIndex != -1) smr.SetBlendShapeWeight(blendShapeIndex, morph.Value * morphMultiplier);
                    }
                }
            }
        }
        
        public void ResetAllBlendshapes()
        {
            if (targetCharacter == null) return;

            var smrs = cachedSMRs != null && cachedSMRs.Length > 0 ? cachedSMRs : targetCharacter.GetComponentsInChildren<SkinnedMeshRenderer>();

            foreach (var smr in smrs)
            {
                if (smr != null && smr.sharedMesh != null)
                {
                    for (int i = 0; i < smr.sharedMesh.blendShapeCount; i++)
                    {
                        smr.SetBlendShapeWeight(i, 0f);
                    }
                }
            }
            
            targetMorphs.Clear(); 
            Debug.Log("[GEi_Receiver] All Blendshapes Reset to 0.");
        }
    }
    
#if UNITY_EDITOR
    [CustomEditor(typeof(GEi_Receiver))]
    public class GEi_Receiver_Editor : Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();

            GEi_Receiver script = (GEi_Receiver)target;

            GUILayout.Space(15);
            
            GUI.backgroundColor = new Color(1f, 0.6f, 0.6f);
            
            if (GUILayout.Button("Reset All Blendshapes to 0", GUILayout.Height(30)))
            {
                script.ResetAllBlendshapes();
                SceneView.RepaintAll();
            }
            
            GUI.backgroundColor = Color.white; 
        }
    }
#endif
}