<div align="center">

<img src="https://github.com/Snifer/DinoSecL4b/blob/main/Dino.png?raw=true" alt="DinosecLabs Logo" width="200"/>

> For English version [English](README-EN.md)

# DinosecLabs

**Plataforma extensible de laboratorios de ethical hacking**
*Aplicaciones vulnerables realistas · Dashboard gamificado · Flags HMAC · Pistas progresivas*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://choosealicense.com/licenses/mit/)
[![Docker](https://img.shields.io/badge/Docker-24%2B-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![OWASP](https://img.shields.io/badge/OWASP-Top%2010%202025-000000?logo=owasp&logoColor=white)](https://owasp.org/Top10/)
[![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)](https://www.python.org/)

</div>

---

## Que es DinosecLabs

DinosecLabs es una **plataforma extensible de entrenamiento en ethical hacking** completamente autocontenida en Docker. Cada laboratorio es una aplicacion con vulnerabilidades ocultas: sin etiquetas, sin pistas en la interfaz, sin ayuda. Lo atacas como un pentester real.

La plataforma arranca con el track **OWASP Top 10 2025** (10 labs, 21 flags) y esta diseñada para crecer: nuevos tracks pueden anadirse de forma independiente sin modificar la infraestructura base.

Cuenta con un **dashboard gamificado** centraliza todo: flags unicas por deployment generadas con HMAC, puedes canjear los DinoCoins por pistas progresivas por niveles y un Salon de la Fama publico impulsado por GitHub Actions.

<div align="center">

Desarrollado por [@Snifer](https://github.com/Snifer) · [sniferl4bs.com](https://sniferl4bs.com)

Si este proyecto te resulta util, considera apoyar su desarrollo:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/sniferl4bs)

</div>

---

## Caracteristicas

| Caracteristica | Descripcion |
|----------------|-------------|
| Laboratorios realistas | 10 aplicaciones  sin ninguna pista en la UI |
| 21 flags ocultas | Solo accesibles explotando la vulnerabilidad correctamente |
| Flags HMAC unicas | `HMAC-SHA256(FLAG_SECRET, vuln_id)[:20]` — unicas por deployment |
| Sistema de monedas | 100–200 monedas por flag completada |
| Hints progresivos | 3 niveles por lab (50 / 75 / 100 monedas, o gratis por progresion) |
| Notas por lab | Bloc integrado con auto-guardado, persistido en SQLite |
| Resetear estado | Reinicia el estado interno del lab sin reconstruir la imagen |
| Progreso exportable | Export CSV detallado desde el dashboard |
| Busqueda y filtro | Filtra labs por estado: Todos / Online / Offline / Completados |
| Health checks HTTP | Distingue entre running y crashed en tiempo real |
| Tiempo activo | Chip HH:MM:SS por lab mientras esta en ejecucion |
| Auto-stop | Detiene labs inactivos automaticamente (por defecto: 4 horas) |
| Salon de la Fama | Via GitHub Issue + GitHub Action automatico |
| Build offline | Todos los paquetes pip incluidos en `packages/` |
| Tracks dinamicos | Nuevos tracks se pueden agregar desde `tracks/mi-track/track.json` |

---

## Dashboard

El dashboard corre en **http://localhost:8000** y tiene cuatro pestanas:

| Pestana | Contenido |
|---------|-----------|
| OWASP Top 10 2025 | Grid de labs: iniciar / detener / enviar flag / hints / notas / reset |
| OWASP API Top 10 | Referencia del API Security Top 10 (labs proximos) |
| Container & K8s | Referencia de vulnerabilidades en contenedores y Kubernetes (labs planificados) |
| About | Informacion del proyecto, desarrollador y roadmap integrado |

---

## Labs OWASP Top 10 2025

**10 laboratorios · 21 flags · maximo 3000 monedas**

| Lab | Categoria | Aplicacion | Puerto |
|-----|-----------|------------|--------|
| A01 | Broken Access Control | CorpHR — Portal de RRHH | 8001 |
| A02 | Security Misconfiguration | DevPortal — Portal DevOps interno | 8002 |
| A03 | Software Supply Chain Failures | PkgManager — Gestor de dependencias | 8003 |
| A04 | Cryptographic Failures | SecureBank — Banca en linea | 8004 |
| A05 | Injection | ShopCorp — Marketplace e-commerce | 8005 |
| A06 | Insecure Design | BizStore — Marketplace B2B | 8006 |
| A07 | Authentication Failures | EmpPortal — Portal de empleados | 8007 |
| A08 | Software & Data Integrity Failures | UpdateHub — Sistema de actualizaciones | 8008 |
| A09 | Security Logging & Alerting Failures | AuditLog — Portal de compliance | 8009 |
| A10 | Mishandling of Exceptional Conditions | DataAPI — API de datos y analytics | 8010 |

---

## Requisitos

| Requisito | Version minima |
|-----------|----------------|
| Docker Engine | 24.x |
| docker-compose | 2.x |
| RAM libre | 2 GB |
| Disco libre | 3 GB |
| Puertos libres | 8000 – 8010 |

---

## Inicio rapido

```bash
git clone https://github.com/Snifer/DinoSecL4b.git
cd DinoSecL4b/owasp-labs
bash setup.sh
```

Abre el dashboard en: **http://localhost:8000**

`setup.sh` detecta el sistema operativo, verifica dependencias, genera el `FLAG_SECRET`, descarga paquetes offline si faltan, construye las imagenes y arranca el dashboard automaticamente.

Actualmente funciona sin problemas en Linux y MacOS si encuentras algún bug o error no dudes en abrir un issue y reportarlo.

---

## Como Usar

```
1. Iniciar un lab          →  boton Start en el dashboard (o ./manage.sh start aXX)
2. Abrir el lab            →  boton Open
3. Explorar la aplicacion     Actua como un pentester real — sin pistas en la UI
4. Explotar la vuln           Encuentra la flag oculta dentro de los datos
5. Enviar la flag          →  boton Flag → pega FLAG{...} → Submit
6. Ganar monedas           →  compra hints si te quedas bloqueado
7. Tomar notas             →  boton Notes — auto-guardado por lab
8. Salon de la Fama        →  Hall of Fame → ingresa tu alias → GitHub Issue
```

---

## Sistema de flags HMAC

Las flags son **unicas por deployment**: derivadas de `HMAC-SHA256(FLAG_SECRET, vuln_id)[:20]`. No pueden compartirse entre instalaciones distintas.

`FLAG_SECRET` se genera automaticamente en `.env` durante el setup.

Para consultar los valores de flags activos en tu instalacion:

```bash
curl http://localhost:8000/api/flag-values
```

---

## Sistema de gamificación

### Monedas por flag

| Dificultad | Monedas | Ejemplos |
|------------|---------|---------|
| Facil | 100 | IDOR, config expuesta, panel oculto |
| Media | 150 | SQLi, JWT forgery, brute force |
| Dificil | 200 | RCE (CMDi, pickle, SSTI) |

### Hints progresivos

Tres niveles por laboratorio:

| Nivel | Coste | Contenido |
|-------|-------|-----------|
| 1 | 50 monedas o gratis* | Direccion general del ataque |
| 2 | 75 monedas | Tecnica especifica a usar |
| 3 | 100 monedas | Pista casi completa |

*El nivel 1 del lab N+1 se desbloquea gratis al enviar cualquier flag del lab N.

### Salon de la Fama

```
1. Dashboard → Hall of Fame → Submit my score
2. Ingresa tu alias → Submit
3. Se abre un GitHub Issue pre-rellenado → haz clic en "Submit new issue"
4. GitHub Action parsea tu puntuacion, actualiza HALL_OF_FAME.md y cierra el issue
```

---

## Gestion desde la terminal

```bash
./manage.sh status          # Ver estado de todos los labs
./manage.sh start a01       # Iniciar un lab especifico
./manage.sh stop a01        # Detener un lab
./manage.sh start-all       # Iniciar todos los labs
./manage.sh logs a05        # Ver logs en tiempo real
./manage.sh build           # Reconstruir todas las imagenes
```

---

## Estructura del proyecto

```
owasp-labs/
├── setup.sh                          # Script de instalacion y arranque
├── manage.sh                         # CLI de gestion de labs
├── docker-compose.yml                # Orquestacion de 11 servicios
├── .env.example
├── packages/                         # Pip wheels para instalacion offline
├── scores.json                       # Datos del Hall of Fame
├── HALL_OF_FAME.md
├── .github/
│   └── workflows/
│       └── hall-of-fame.yml          # GitHub Action: procesa issues de puntuacion
├── tracks/
│   └── owasp-top10-2025/
│       └── track.json
├── dashboard/
│   ├── app.py                        # Flask + Docker SDK + SQLite
│   ├── Dockerfile
│   └── templates/
│       └── index.html                # UI completa del dashboard
└── labs/
    ├── a01-broken-access-control/
    ├── a02-security-misconfiguration/
    ├── a03-supply-chain/
    ├── a04-cryptographic-failures/
    ├── a05-injection/
    ├── a06-insecure-design/
    ├── a07-auth-failures/
    ├── a08-integrity-failures/
    ├── a09-logging-failures/
    └── a10-exceptional-conditions/
```

---

## Solucion de problemas

### El dashboard no arranca

```bash
# Verificar que Docker esta en ejecucion
docker info

# Revisar los logs del dashboard
docker compose logs dashboard

# Comprobar que los puertos 8000-8010 estan libres
ss -tlnp | grep -E '800[0-9]|8010'
```

### Un lab no inicia o aparece como crashed

```bash
# Ver logs del lab especifico (ejemplo: A01)
docker compose logs a01-broken-access-control

# Reiniciar solo ese lab
docker compose restart a01-broken-access-control

# O desde la terminal de gestion
./manage.sh start a01
```

### Las flags no son validadas

Las flags son unicas por deployment. Si reinstalaste o regeneraste el `.env`, las flags cambian. Consulta los valores actuales:

```bash
curl http://localhost:8000/api/flag-values
```

Si el archivo `.env` fue eliminado, ejecuta `bash setup.sh` de nuevo para regenerar `FLAG_SECRET`. Las flags anteriores quedaran invalidadas.

### Error de permisos en setup.sh

```bash
chmod +x setup.sh manage.sh
bash setup.sh
```

### Error de DNS o paquetes durante el build

Los paquetes pip estan incluidos en `packages/` — el build es completamente offline. Si necesitas regenerarlos:

```bash
pip3 download flask docker pyjwt \
  -d packages/ \
  --platform manylinux2014_x86_64 \
  --python-version 312 \
  --only-binary=:all:
```

### Falta de espacio en disco o RAM

```bash
docker system df
free -h
```

Usa el dashboard para iniciar solo los labs necesarios en cada sesion. El auto-stop (4h por defecto) libera recursos automaticamente.

### Reinstalar desde cero

```bash
docker compose down -v --remove-orphans
docker system prune -f
bash setup.sh
```

### Reiniciar el progreso

```bash
# Desde el dashboard → boton Reset progress
# O via API:
curl -X POST http://localhost:8000/api/reset
```

---

## Contribuciones

Las contribuciones son bienvenidas: nuevos labs, nuevos tracks, traducciones y correcciones de bugs.

### Como contribuir un track nuevo

1. Haz fork del repositorio
2. Crea una rama: `git checkout -b feature/mi-track`
3. Crea la estructura en `tracks/mi-track/` con el formato siguiente
4. Asegurate de que cada lab tenga su propio `Dockerfile` y sea autocontenido
5. Abre un Pull Request describiendo el track, vulnerabilidades cubiertas y flags incluidas

### Estructura de track.json

```json
{
  "id": "mi-track",
  "name": "Nombre del Track",
  "description": "Descripcion del track",
  "labs": [
    {
      "id": "lab-id",
      "name": "Nombre del Lab",
      "description": "Descripcion breve",
      "category": "Categoria OWASP",
      "port": 8011,
      "service": "nombre-servicio-docker",
      "flags": [
        {
          "id": "vuln_id_unico",
          "description": "Descripcion de la vulnerabilidad",
          "points": 150,
          "hints": [
            "Hint nivel 1 (direccion general)",
            "Hint nivel 2 (tecnica especifica)",
            "Hint nivel 3 (pista detallada)"
          ]
        }
      ]
    }
  ]
}
```

### Estructura de directorios para un track nuevo

```
tracks/
└── mi-track/
    ├── track.json
    └── labs/
        └── lab-01/
            ├── Dockerfile
            └── app/
```

Para reportar bugs o proponer mejoras, abre un [Issue en GitHub](https://github.com/Snifer/DinoSecL4b/issues).

---

## Roadmap de tracks

| Track | Estado |
|-------|--------|
| OWASP Top 10 2025 | Disponible |
| OWASP API Security Top 10 | Proximamente |
| Cloud Security Fundamentals | Planificado |
| Container & Kubernetes Security | Planificado |
| Active Directory Attacks | En consideracion |
| Mobile Security (Android) | En consideracion |
| Cert Prep: eJPT / OSCP / CEH | En consideracion |

---

## Aviso legal

Este laboratorio se proporciona **unicamente con fines educativos y de entrenamiento en ethical hacking**. No esta destinado para uso en entornos de produccion. Utilizalo de manera etica y responsable, unicamente sobre sistemas propios o con autorizacion expresa.

---

## Licencia

[MIT](https://choosealicense.com/licenses/mit/) — consulta el archivo `LICENSE` para mas detalles.

---

<div align="center">

Desarrollado por [@Snifer](https://github.com/Snifer) · [sniferl4bs.com](https://sniferl4bs.com)

Si este proyecto te resulta util, considera apoyar su desarrollo:

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/sniferl4bs)

</div>
