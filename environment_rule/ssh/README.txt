用途：说明 GiteeRepo 测试环境私钥的本机放置方式。

获授权成员可将私钥放在 `ssh/hermes_ed25519`。该目录已被 Git 忽略；使用前
必须通过父目录的 `known_hosts` 校验目标主机身份，禁止提交私钥或其他密钥材料。

Purpose: local private-key placement for the GiteeRepo test environment.

Put the authorized private key at ssh/hermes_ed25519 on each approved machine.
This file is ignored by Git. Its matching public host identities are stored in
the parent known_hosts file and must be verified before use.
