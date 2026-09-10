import os

def blob_callback(blob, metadata):
    if blob.original_size > 100 * 1024 * 1024:  # taille > 100 Mo
        print(f"Removing blob {metadata.blob_id.hex()} of size {blob.original_size}")
        blob.skip()

def blob_callback(blob, metadata):
    max_size = 100 * 1024 * 1024  # 100 Mo en octets
    if blob.size > max_size:
        print(f"Removing blob {metadata.sha} of size {blob.size}")
        return None  # supprime le blob
    return blob.data  # conserve le blob sinon
