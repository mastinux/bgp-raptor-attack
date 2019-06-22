# ==============================================================================
# directory authority
# ==============================================================================
sed -i 's/Address 127.0.0.1/Address 15.3.0.1/g' ~/chutney/net/nodes/000authority/torrc

# ==============================================================================
# exit relay
# ==============================================================================
sed -i 's/127.0.0.1:7000/15.3.0.1:7000/g' ~/chutney/net/nodes/001guard/torrc
sed -i 's/OrPort 5001/OrPort 5000/g' ~/chutney/net/nodes/001guard/torrc
sed -i 's/Address 127.0.0.1/Address 12.2.0.1/g' ~/chutney/net/nodes/001guard/torrc
sed -i 's/DirPort 7001/DirPort 7000/g' ~/chutney/net/nodes/001guard/torrc
sed -i 's/ControlPort 8001/ControlPort 8000/g' ~/chutney/net/nodes/001guard/torrc

# ==============================================================================
# exit relay
# ==============================================================================
sed -i 's/127.0.0.1:7000/15.3.0.1:7000/g' ~/chutney/net/nodes/002exit/torrc
sed -i 's/OrPort 5002/OrPort 5000/g' ~/chutney/net/nodes/002exit/torrc
sed -i 's/Address 127.0.0.1/Address 16.2.0.1/g' ~/chutney/net/nodes/002exit/torrc
sed -i 's/127.0.0.0\/8/16.2.0.1\/8/g' ~/chutney/net/nodes/002exit/torrc
sed -i 's/DirPort 7002/DirPort 7000/g' ~/chutney/net/nodes/002exit/torrc
sed -i 's/ControlPort 8002/ControlPort 8000/g' ~/chutney/net/nodes/002exit/torrc

# ==============================================================================
# client
# ==============================================================================
sed -i 's/127.0.0.1:7000/15.3.0.1:7000/g' ~/chutney/net/nodes/003client/torrc
sed -i 's/ControlPort 8003/ControlPort 8000/g' ~/chutney/net/nodes/003client/torrc
sed -i 's/SocksPort 9003/SocksPort 9000/g' ~/chutney/net/nodes/003client/torrc

