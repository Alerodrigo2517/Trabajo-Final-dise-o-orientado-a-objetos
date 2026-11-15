import bcrypt


def hash_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("La contraseña debe tener 8 caracteres, como mínimo.")

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
"""  ----"""