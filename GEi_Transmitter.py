import RLPy
import socket
import struct
import ctypes
import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *

# Ensure global socket persistence
if 'gei_sock' not in globals():
    gei_sock = None

class GEiDashboard(QWidget):
    def __init__(self):
        super(GEiDashboard, self).__init__()
        self.setWindowTitle("GEi Transmitter (V1.0 - Open Source Release)")
        # Increased window width to accommodate the individual port inputs
        self.setGeometry(100, 100, 480, 250)
        self.setWindowFlags(Qt.WindowStaysOnTopHint) 
        
        main_layout = QVBoxLayout()
        
        self.title_label = QLabel("<b>Team Gadget : GEi Transmitter<br><font color='#00C853' size='2'>(Core Synchronization Module - Multi-Stream)</font></b>")
        self.title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.title_label)

        # Avatar List & Link ID & Port Input
        self.avatar_list_group = QGroupBox("=== Target Characters (Link ID & Port) ===")
        self.avatar_list_layout = QVBoxLayout()
        self.avatar_inputs = [] 
        
        self.refresh_avatar_list()
        
        self.avatar_list_group.setLayout(self.avatar_list_layout)
        main_layout.addWidget(self.avatar_list_group)

        self.status_label = QLabel("Status: <font color='red'>STOPPED</font>")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        self.start_btn = QPushButton("START STREAM")
        self.start_btn.setStyleSheet("background-color: #2E7D32; color: white; font-weight: bold; padding: 10px;")
        self.start_btn.clicked.connect(self.start_stream)
        main_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("STOP STREAM")
        self.stop_btn.setStyleSheet("background-color: #C62828; color: white; font-weight: bold; padding: 10px;")
        self.stop_btn.clicked.connect(self.stop_stream)
        main_layout.addWidget(self.stop_btn)

        # Hybrid Mode Toggle (Applies globally to all active streams)
        self.face_only_cb = QCheckBox("Hybrid Mode (Neck, Head & Morphs ONLY)")
        self.face_only_cb.setStyleSheet("color: #FF9800; font-weight: bold; padding-top: 5px;")
        main_layout.addWidget(self.face_only_cb)
        
        self.setLayout(main_layout)

        # Windows API Timer Setup
        self.HWND = ctypes.c_void_p
        self.UINT = ctypes.c_uint
        self.UINT_PTR = ctypes.c_uint64 if sys.maxsize > 2**32 else ctypes.c_uint
        self.DWORD = ctypes.c_ulong
        self.TIMERPROC = ctypes.WINFUNCTYPE(None, self.HWND, self.UINT, self.UINT_PTR, self.DWORD)
        self.user32 = ctypes.windll.user32
        self.user32.SetTimer.argtypes = [self.HWND, self.UINT_PTR, self.UINT, self.TIMERPROC]
        self.user32.SetTimer.restype = self.UINT_PTR
        self.user32.KillTimer.argtypes = [self.HWND, self.UINT_PTR]
        self.user32.KillTimer.restype = ctypes.c_bool
        
        self.timer_id = None
        self.timer_func = self.TIMERPROC(self.tick_stream) 
        
        # List to hold configuration for each actively streaming character
        self.active_streams = []
        self.is_streaming = False

    def refresh_avatar_list(self):
        avatars = RLPy.RScene.GetAvatars()
        if len(avatars) == 0:
            self.avatar_list_layout.addWidget(QLabel("No Characters in Scene..."))
            return

        default_port = 8990
        for i, av in enumerate(avatars):
            row = QHBoxLayout()
            
            name_label = QLabel(f"{av.GetName()}")
            name_label.setFixedWidth(120)
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText("Paste Unity Link ID...")
            
            port_label = QLabel("Port:")
            port_edit = QLineEdit(str(default_port + i))
            port_edit.setFixedWidth(50)
            
            row.addWidget(name_label)
            row.addWidget(line_edit)
            row.addWidget(port_label)
            row.addWidget(port_edit)
            
            self.avatar_list_layout.addLayout(row)
            self.avatar_inputs.append({
                'avatar': av, 
                'line_edit': line_edit,
                'port_edit': port_edit
            })

    def start_stream(self):
        global gei_sock
        
        self.active_streams = []
        
        for item in self.avatar_inputs:
            link_id_text = item['line_edit'].text().strip()
            port_text = item['port_edit'].text().strip()
            
            if not link_id_text or not port_text:
                continue
                
            try:
                target_port = int(port_text)
            except ValueError:
                self.status_label.setText("Error: <font color='red'>Invalid Port detected!</font>")
                return

            avatar = item['avatar']
            char_id_bytes = link_id_text.encode('utf-8')
            skeleton = avatar.GetSkeletonComponent()
            bones = skeleton.GetSkinBones()
            
            if self.face_only_cb.isChecked():
                target_bone_names = [
                    "CC_Base_NeckTwist01", "CC_Base_NeckTwist02", "CC_Base_Head",
                    "CC_Base_FacialBone", "CC_Base_JawRoot", "CC_Base_Teeth02", 
                    "CC_Base_Tongue01", "CC_Base_Tongue02", "CC_Base_Tongue03",
                    "CC_Base_L_Eye", "CC_Base_R_Eye", "CC_Base_UpperJaw", "CC_Base_Teeth01"
                ]
                target_bones = []
            else:
                target_bone_names = [
                    "CC_Base_BoneRoot", "CC_Base_Hip", "CC_Base_Pelvis",
                    "CC_Base_L_Thigh", "CC_Base_L_Calf", "CC_Base_L_CalfTwist01", "CC_Base_L_CalfTwist02", "CC_Base_L_Foot", "CC_Base_L_ToeBase",
                    "CC_Base_L_BigToe1", "CC_Base_L_IndexToe1", "CC_Base_L_MidToe1", "CC_Base_L_PinkyToe1", "CC_Base_L_RingToe1",
                    "CC_Base_L_ToeBaseShareBone", "CC_Base_L_KneeShareBone", "CC_Base_L_ThighTwist01", "CC_Base_L_ThighTwist02",
                    "CC_Base_R_Thigh", "CC_Base_R_Calf", "CC_Base_R_CalfTwist01", "CC_Base_R_CalfTwist02", "CC_Base_R_Foot", "CC_Base_R_ToeBase",
                    "CC_Base_R_BigToe1", "CC_Base_R_IndexToe1", "CC_Base_R_MidToe1", "CC_Base_R_PinkyToe1", "CC_Base_R_RingToe1",
                    "CC_Base_R_ToeBaseShareBone", "CC_Base_R_KneeShareBone", "CC_Base_R_ThighTwist01", "CC_Base_R_ThighTwist02",
                    "CC_Base_Waist", "CC_Base_Spine01", "CC_Base_Spine02",
                    "CC_Base_L_Clavicle", "CC_Base_L_Upperarm", "CC_Base_L_Forearm", "CC_Base_L_ElbowShareBone", "CC_Base_L_ForearmTwist01", "CC_Base_L_ForearmTwist02", "CC_Base_L_Hand",
                    "CC_Base_L_Index1", "CC_Base_L_Index2", "CC_Base_L_Index3",
                    "CC_Base_L_Mid1", "CC_Base_L_Mid2", "CC_Base_L_Mid3",
                    "CC_Base_L_Pinky1", "CC_Base_L_Pinky2", "CC_Base_L_Pinky3",
                    "CC_Base_L_Ring1", "CC_Base_L_Ring2", "CC_Base_L_Ring3",
                    "CC_Base_L_Thumb1", "CC_Base_L_Thumb2", "CC_Base_L_Thumb3",
                    "CC_Base_L_UpperarmTwist01", "CC_Base_L_UpperarmTwist02", "CC_Base_L_RibsTwist", "CC_Base_L_Breast",
                    "CC_Base_NeckTwist01", "CC_Base_NeckTwist02", "CC_Base_Head",
                    "CC_Base_FacialBone", "CC_Base_JawRoot", "CC_Base_Teeth02", "CC_Base_Tongue01", "CC_Base_Tongue02", "CC_Base_Tongue03",
                    "CC_Base_L_Eye", "CC_Base_R_Eye", "CC_Base_UpperJaw", "CC_Base_Teeth01",
                    "CC_Base_R_Clavicle", "CC_Base_R_Upperarm", "CC_Base_R_Forearm", "CC_Base_R_ElbowShareBone", "CC_Base_R_ForearmTwist01", "CC_Base_R_ForearmTwist02", "CC_Base_R_Hand",
                    "CC_Base_R_Index1", "CC_Base_R_Index2", "CC_Base_R_Index3",
                    "CC_Base_R_Mid1", "CC_Base_R_Mid2", "CC_Base_R_Mid3",
                    "CC_Base_R_Pinky1", "CC_Base_R_Pinky2", "CC_Base_R_Pinky3",
                    "CC_Base_R_Ring1", "CC_Base_R_Ring2", "CC_Base_R_Ring3",
                    "CC_Base_R_Thumb1", "CC_Base_R_Thumb2", "CC_Base_R_Thumb3",
                    "CC_Base_R_UpperarmTwist01", "CC_Base_R_UpperarmTwist02", "CC_Base_R_RibsTwist", "CC_Base_R_Breast"
                ]
                target_bones = []
                
                bone_root = None
                for b in bones:
                    if b.GetName() in ["CC_Base_Hip", "CC_Base_Pelvis"]:
                        current_parent = b.GetParent()
                        while current_parent is not None:
                            if "BoneRoot" in current_parent.GetName():
                                bone_root = current_parent
                                break
                            current_parent = current_parent.GetParent()
                        if bone_root:
                            break
                if bone_root:
                    target_bones.append(bone_root)

            for name in target_bone_names:
                for b in bones:
                    if b.GetName() == name and b not in target_bones:
                        target_bones.append(b)
                        break

            cached_morph_names = []
            morph_cooldowns = {} 
            
            try:
                if hasattr(avatar, "GetFaceComponent"):
                    face_comp = avatar.GetFaceComponent()
                    if face_comp:
                        try:
                            names_main = face_comp.GetExpressionNames("")
                            if names_main: cached_morph_names.extend(names_main)
                        except: pass
                        try:
                            names_custom = face_comp.GetExpressionNames("Custom")
                            if names_custom: cached_morph_names.extend(names_custom)
                        except: pass
            except Exception:
                pass
                
            self.active_streams.append({
                'avatar': avatar,
                'char_id_bytes': char_id_bytes,
                'port': target_port,
                'target_bones': target_bones,
                'cached_morph_names': cached_morph_names,
                'morph_cooldowns': morph_cooldowns
            })
            
        if not self.active_streams:
            self.status_label.setText("Error: <font color='red'>No valid Link IDs provided!</font>")
            return

        if gei_sock is None:
            gei_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
        self.status_label.setText(f"Status: <font color='green'>STREAMING ({len(self.active_streams)} Targets)</font>")
        self.is_streaming = True
        
        if self.timer_id is None:
            self.timer_id = self.user32.SetTimer(None, 0, 16, self.timer_func)

    def stop_stream(self):
        self.is_streaming = False
        if self.timer_id is not None:
            self.user32.KillTimer(None, self.timer_id)
            self.timer_id = None
        self.status_label.setText("Status: <font color='red'>STOPPED</font>")

    def tick_stream(self, hwnd, msg, timer_id, current_time):
        if not self.is_streaming: return
            
        global gei_sock
        if gei_sock is None: return

        UDP_IP = "127.0.0.1"
        kTime = RLPy.RGlobal.GetTime()
        
        for stream in self.active_streams:
            avatar = stream['avatar']
            char_id_bytes = stream['char_id_bytes']
            target_bones = stream['target_bones']
            cached_morph_names = stream['cached_morph_names']
            morph_cooldowns = stream['morph_cooldowns']
            target_port = stream['port']
            
            try:
                payload = bytearray(b'GICB')
                payload.append(1)
                payload.append(len(char_id_bytes))
                payload.extend(char_id_bytes)
                
                rtx, rty, rtz = 0.0, 0.0, 0.0
                rrx, rry, rrz, rrw = 0.0, 0.0, 0.0, 1.0
                
                try:
                    transform_ctrl = avatar.GetControl("Transform")
                    if transform_ctrl:
                        wt = transform_ctrl.GetValue(kTime)
                        rt = wt.T()
                        rr = wt.R()
                        rtx, rty, rtz = rt.x, rt.y, rt.z
                        rrx, rry, rrz, rrw = rr.x, rr.y, rr.z, rr.w
                except Exception:
                    pass

                payload.extend(struct.pack('<fff', rtx, rty, rtz))
                payload.extend(struct.pack('<ffff', rrx, rry, rrz, rrw))
                
                payload.append(len(target_bones))
                for bone in target_bones:
                    name_bytes = bone.GetName().encode('utf-8')
                    payload.append(len(name_bytes))
                    payload.extend(name_bytes)
                    payload.append(3) 
                    
                    t = bone.LocalTransform().T()
                    r = bone.LocalTransform().R()

                    payload.extend(struct.pack('<fff', t.x, t.y, t.z))
                    payload.extend(struct.pack('<ffff', r.x, r.y, r.z, r.w))
                
                morph_payload = bytearray()
                active_morph_count = 0
                current_morph_cooldowns = {}
                
                if cached_morph_names and hasattr(avatar, "GetFaceComponent"):
                    try:
                        face_comp = avatar.GetFaceComponent()
                        if face_comp:
                            res = face_comp.GetExpressionWeights(kTime, cached_morph_names)
                            weights = res[1] if (isinstance(res, tuple) and len(res) == 2) else res
                            
                            if weights and len(weights) >= len(cached_morph_names):
                                for i in range(len(cached_morph_names)):
                                    m_name = cached_morph_names[i]
                                    weight = float(weights[i])
                                    is_active = abs(weight) > 0.001
                                    
                                    if is_active:
                                        current_morph_cooldowns[m_name] = 5
                                        m_name_bytes = m_name.encode('utf-8')
                                        if len(m_name_bytes) < 255:
                                            morph_payload.append(len(m_name_bytes))
                                            morph_payload.extend(m_name_bytes)
                                            morph_payload.extend(struct.pack('<f', weight))
                                            active_morph_count += 1
                                            if active_morph_count >= 255: break
                                            
                                    else:
                                        cooldown = morph_cooldowns.get(m_name, 0)
                                        if cooldown > 0:
                                            current_morph_cooldowns[m_name] = cooldown - 1
                                            m_name_bytes = m_name.encode('utf-8')
                                            if len(m_name_bytes) < 255:
                                                morph_payload.append(len(m_name_bytes))
                                                morph_payload.extend(m_name_bytes)
                                                morph_payload.extend(struct.pack('<f', 0.0))
                                                active_morph_count += 1
                                                if active_morph_count >= 255: break
                    except Exception:
                        pass

                stream['morph_cooldowns'] = current_morph_cooldowns
                payload.append(active_morph_count)
                if active_morph_count > 0:
                    payload.extend(morph_payload)
                
                gei_sock.sendto(payload, (UDP_IP, target_port))
            except Exception:
                pass

    def closeEvent(self, event):
        self.stop_stream()
        super(GEiDashboard, self).closeEvent(event)

app = QApplication.instance()
if not app: app = QApplication([])
if hasattr(RLPy, "gei_window") and RLPy.gei_window is not None: RLPy.gei_window.close()
RLPy.gei_window = GEiDashboard()
RLPy.gei_window.show()