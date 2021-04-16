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
   http://localhost:8080/<your_login>
```

Access personalized message:

```bash
curl -b session http://localhost:8080/
```
