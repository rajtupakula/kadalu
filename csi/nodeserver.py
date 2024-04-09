"""
nodeserver implementation
"""
import logging
import os
import time

import csi_pb2
import csi_pb2_grpc
import grpc
from threading import Lock

mount_lock = Lock()

class NodeServer(csi_pb2_grpc.NodeServicer):
    # Existing methods...

    def NodePublishVolume(self, request, context):
        with mount_lock:
            # Volume mounting logic...
            if mount_volume(pvpath_full, request.target_path, pvtype, fstype=None):
                # Operation success
                ...
            else:
                # Handle error
                ...

    def NodeUnpublishVolume(self, request, context):
        with mount_lock:
            # Volume unmounting logic...
            unmount_volume(request.target_path)
            # Additional logic...

            "NodeExpandVolume called, which is not implemented."
        ))

        return csi_pb2.NodeExpandVolumeResponse()
