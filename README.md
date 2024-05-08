### Exécution avec Docker

```bash
docker build -t tst_app --progress=plain .
```

Puis

```bash
docker run -p 8501:8501 tst_app
```
