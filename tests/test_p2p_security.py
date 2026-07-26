from src.modules.net.p2p_security import P2PNetworkSecurity


def test_p2p_network_security_init():
    security = P2PNetworkSecurity()
    assert security.is_secure is False


def test_p2p_network_security_initialize():
    security = P2PNetworkSecurity()
    security.initialize_security()
    assert security.is_secure is False


def test_p2p_network_security_get_status():
    security = P2PNetworkSecurity()
    assert security.get_status() is False
