import bcrypt


def hash_password(contrasena: str) -> str:
    if len(contrasena) < 8:
        raise ValueError("La contraseña debe tener 8 caracteres, como mínimo.")

    hash_calculado = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt())
    return hash_calculado.decode("utf-8")


def verify_password(contrasena: str, hash_contrasena: str) -> bool:
    return bcrypt.checkpw(
        contrasena.encode("utf-8"),
        hash_contrasena.encode("utf-8"),
    )
"""  ----"""