from pywallet.utils import Wallet, HDPrivateKey, HDKey
from pywallet.utils.bip32 import *
from pywallet.wallet import generate_mnemonic, create_address


class DucatusMainNet(object):
    NAME = "Ducatus Main Net"
    COIN = "DUC"
    SCRIPT_ADDRESS = 0x06  # int(0x06) = 6
    PUBKEY_ADDRESS = 0x31  # int(0x31) = 48
    SECRET_KEY = PUBKEY_ADDRESS + 128  # = int(0xb1) = 177
    EXT_PUBLIC_KEY = 0x0488B21E
    EXT_SECRET_KEY = 0x0488ADE4
    BIP32_PATH = "m/44'/0'/0'/"


class DucatusWallet(Wallet):

    @classmethod
    def get_network(self, network):
        return DucatusMainNet

    @classmethod
    def from_master_secret(cls, seed, network='ducatus'):
        network = DucatusWallet.get_network(network)
        seed = ensure_bytes(seed)
        # Given a seed S of at least 128 bits, but 256 is advised
        # Calculate I = HMAC-SHA512(key="Bitcoin seed", msg=S)
        I = hmac.new(b"Bitcoin seed", msg=seed, digestmod=sha512).digest()
        # Split I into two 32-byte sequences, IL and IR.
        I_L, I_R = I[:32], I[32:]
        # Use IL as master secret key, and IR as master chain code.
        return cls(private_exponent=long_or_int(hexlify(I_L), 16),
                   chain_code=long_or_int(hexlify(I_R), 16),
                   network=network)

    @classmethod  # @memoize
    def deserialize(cls, key, network="ducatus"):
        network = DucatusWallet.get_network(network)

        if len(key) in [78, (78 + 32)]:
            # we have a byte array, so pass
            pass
        else:
            key = ensure_bytes(key)
            if len(key) in [78 * 2, (78 + 32) * 2]:
                # we have a hexlified non-base58 key, continue!
                key = unhexlify(key)
            elif len(key) == 111:
                # We have a base58 encoded string
                key = base58.b58decode_check(key)
        # Now that we double checkd the values, convert back to bytes because
        # they're easier to slice
        version, depth, parent_fingerprint, child, chain_code, key_data = (
            key[:4], key[4], key[5:9], key[9:13], key[13:45], key[45:])

        version_long = long_or_int(hexlify(version), 16)
        exponent = None
        pubkey = None
        point_type = key_data[0]
        if not isinstance(point_type, six.integer_types):
            point_type = ord(point_type)
        if point_type == 0:
            # Private key
            if version_long != network.EXT_SECRET_KEY:
                raise incompatible_network_exception_factory(
                    network.NAME, network.EXT_SECRET_KEY,
                    version)
            exponent = key_data[1:]
        elif point_type in [2, 3, 4]:
            # Compressed public coordinates
            if version_long != network.EXT_PUBLIC_KEY:
                raise incompatible_network_exception_factory(
                    network.NAME, network.EXT_PUBLIC_KEY,
                    version)
            pubkey = PublicKey.from_hex_key(key_data, network=network)
            # Even though this was generated from a compressed pubkey, we
            # want to store it as an uncompressed pubkey
            pubkey.compressed = False
        else:
            raise ValueError("Invalid key_data prefix, got %s" % point_type)

        def l(byte_seq):
            if byte_seq is None:
                return byte_seq
            elif isinstance(byte_seq, six.integer_types):
                return byte_seq
            return long_or_int(hexlify(byte_seq), 16)

        return cls(depth=l(depth),
                   parent_fingerprint=l(parent_fingerprint),
                   child_number=l(child),
                   chain_code=l(chain_code),
                   private_exponent=l(exponent),
                   public_key=pubkey,
                   network=network)
