import redis
import json

r = redis.Redis(host='34.70.122.249', port=6379, password='Chibuikem2025', decode_responses=True)

print("=== SERVER INFO (keyspace) ===")
try:
    info = r.info('keyspace')
    print(json.dumps(info, indent=2))
except Exception as e:
    print(f"Error getting info: {e}")

print("\n=== ALL KEYS ===")
try:
    keys = r.keys('*')
    for k in sorted(keys):
        print(k)
    print(f"\nTotal keys: {len(keys)}")
except Exception as e:
    print(f"Error getting keys: {e}")
    keys = []

print("\n=== PERMISSION KEYS ===")
try:
    perm_keys = r.keys('permission*')
    for k in sorted(perm_keys):
        ttl = r.ttl(k)
        val = r.get(k) if r.type(k) == 'string' else r.hgetall(k)
        print(f"Key: {k}")
        print(f"  TTL: {ttl}s")
        print(f"  Value: {val}")
except Exception as e:
    print(f"Error getting permission keys: {e}")

print("\n=== KAFKA CONFIG CACHE KEYS ===")
try:
    kafka_keys = r.keys('kafka_config*')
    for k in sorted(kafka_keys):
        ttl = r.ttl(k)
        val = r.get(k)
        print(f"Key: {k}  TTL: {ttl}s")
        try:
            parsed = json.loads(val)
            # Mask password
            if 'sasl_plain_password' in parsed: parsed['sasl_plain_password'] = '***'
            if 'password' in parsed: parsed['password'] = '***'
            if 'sasl_password' in parsed: parsed['sasl_password'] = '***'
            print(f"  Value: {json.dumps(parsed, indent=4)}")
        except:
            print(f"  Value: {val}")
except Exception as e:
    print(f"Error getting kafka keys: {e}")

print("\n=== ALL KEYS WITH TYPE + TTL ===")
for k in sorted(keys):
    try:
        ktype = r.type(k)
        ttl = r.ttl(k)
        print(f"  [{ktype:10s}] TTL={ttl:7}s  {k}")
    except Exception as e:
        print(f"  Error getting info for {k}: {e}")
