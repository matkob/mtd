# Moving Target Defence PoC

## Web Application

### Testing sessions

Create session storage:

```bash
touch session
```

Log in:

```bash
curl -X PUT \
  -c session \
  -b session \
   http://localhost:8080/login/<your_login>
   
# Response: 
#   500 - error 
#   202 - accepted
```

Access personalized message:

```bash
curl -b session http://localhost:8080/

# Response: 
#   500 - error 
#   200 - OK
```

## Session Manager

Create new session:

```bash
curl -X PUT \
  -d '<json_data>' \
  -H "Content-Type: Application/json" \
  http://localhost:8888/session/<session_id>
  
# Response: 
#   202 - accepted
#   400 - bad request
```

Access session data:

```bash
curl http://localhost:8888/session/<session_id>

# Response: 
#   200 - OK
#   404 - not found
```
