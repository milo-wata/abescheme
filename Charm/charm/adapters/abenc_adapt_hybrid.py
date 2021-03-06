
from charm.toolbox.ABEnc import ABEnc
from charm.schemes.abenc.abenc_bsw07 import CPabe_BSW07
from charm.toolbox.pairinggroup import PairingGroup,GT
from charm.toolbox.symcrypto import AuthenticatedCryptoAbstraction
from charm.core.math.pairing import hashPair as sha1
from math import ceil

debug = False
class HybridABEnc(ABEnc):
    """
    >>> group = PairingGroup("SS512")
    >>> cpabe = CPabe_BSW07(group)
    >>> hyb_abe = HybridABEnc(cpabe, group)
    >>> access_policy = '((four or three) and (two or one))'
    >>> msg = "hello world this is an important message."
    >>> (master_public_key, master_key) = hyb_abe.setup()
    >>> secret_key = hyb_abe.keygen(master_public_key, master_key, ['ONE', 'TWO', 'THREE'])
    >>> cipher_text = hyb_abe.encrypt(master_public_key, msg, access_policy)
    >>> hyb_abe.decrypt(master_public_key, secret_key, cipher_text)
    'hello world this is an important message.'
    """
    def __init__(self, scheme, groupObj):
        ABEnc.__init__(self)
        global abenc
        # check properties (TODO)
        abenc = scheme
        self.group = groupObj
            
    def setup(self):
        return abenc.setup()
    
    def keygen(self, pk, mk, object):
        return abenc.keygen(pk, mk, object)
    
    def encrypt(self, pk, M, object):
        key = self.group.random(GT)
        c1 = abenc.encrypt(pk, key, object)
        # instantiate a symmetric enc scheme from this key
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        c2 = cipher.encrypt(M)
        return { 'c1':c1, 'c2':c2 }
    
    def decrypt(self, pk, sk, ct):
        c1, c2 = ct['c1'], ct['c2']
        key = abenc.decrypt(pk, sk, c1)
        print type(key), key
        cipher = AuthenticatedCryptoAbstraction(sha1(key))
        print cipher
        return cipher.decrypt(c2)
    
def main():
    groupObj = PairingGroup('SS512')
    cpabe = CPabe_BSW07(groupObj)
    hyb_abe = HybridABEnc(cpabe, groupObj)
    #access_policy = "((ADS or PVB or ME) and (720 or 168 or 24 or 1) and (SITE) and (KEEP) and (TRACK) and (LOCATE))"
    access_policy = "(ADS or PVB or ME) and (720 or 168 or 24 or 1) and SITE"
    message = "hello world this is an important message."
    (pk, mk) = hyb_abe.setup()
    if debug: print("pk => ", pk)
    if debug: print("mk => ", mk)
    sk = hyb_abe.keygen(pk, mk, ['ADS', '720', 'KEEP', 'TARGET', 'TRACK', 'NOLOCATE'])
    if debug: print("sk => ", sk)
    ct = hyb_abe.encrypt(pk, message, access_policy)
    mdec = hyb_abe.decrypt(pk, sk, ct)
    assert mdec == message, "Failed Decryption!!!"
    if debug: print("Successful Decryption!!!")

if __name__ == "__main__":
    debug = True
    main()
