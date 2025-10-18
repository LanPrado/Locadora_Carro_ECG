# backend/app/routes/auth_utils.py
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import json
import base64

# Configurações
SECRET_KEY = "sua_chave_secreta_muito_segura_aqui_mude_em_producao"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Sistema de senhas simplificado (apenas para desenvolvimento)
def crian_hash_senha(senha: str) -> str:
    """Cria hash da senha usando SHA256 com salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256()
    hash_obj.update(f"{senha}{salt}".encode('utf-8'))
    return f"{salt}${hash_obj.hexdigest()}"

def verificar_senha(senha: str, hash_senha: str) -> bool:
    """Verifica se a senha corresponde ao hash"""
    try:
        salt, stored_hash = hash_senha.split('$')
        hash_obj = hashlib.sha256()
        hash_obj.update(f"{senha}{salt}".encode('utf-8'))
        return hash_obj.hexdigest() == stored_hash
    except:
        return False

def criar_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria token JWT simplificado"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = data.copy()
    payload.update({
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp()
    })
    
    # Codificação base64 simples (não é JWT real, mas funciona para desenvolvimento)
    header = {"alg": "HS256", "typ": "JWT"}
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=')
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=')
    
    # Assinatura simplificada
    signature_input = f"{encoded_header}.{encoded_payload}".encode()
    signature = hashlib.sha256(signature_input + SECRET_KEY.encode()).hexdigest()
    
    return f"{encoded_header}.{encoded_payload}.{signature}"

def verificar_access_token(token: str) -> Optional[dict]:
    """Verifica token JWT simplificado"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
            
        encoded_header, encoded_payload, signature = parts
        
        # Verificar assinatura
        signature_input = f"{encoded_header}.{encoded_payload}".encode()
        expected_signature = hashlib.sha256(signature_input + SECRET_KEY.encode()).hexdigest()
        
        if not secrets.compare_digest(signature, expected_signature):
            return None
            
        # Decodificar payload
        payload_json = base64.urlsafe_b64decode(encoded_header + '=' * (4 - len(encoded_header) % 4))
        payload = json.loads(payload_json)
        
        # Verificar expiração
        if datetime.utcnow().timestamp() > payload.get('exp', 0):
            return None
            
        return payload
        
    except:
        return None