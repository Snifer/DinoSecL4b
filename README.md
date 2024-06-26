
# Dino Security Lab

Este proyecto proporciona una infraestructura rápida y sencilla para configurar un laboratorio de pentesting vulnerable utilizando Docker. 

Permite a todo aquel que desea aprender y practicar realizar pruebas y prácticas de pentesting web e infraestructura de manera segura.

<p align="center">
<img src="https://github.com/Snifer/DinoSecL4b/blob/main/Dino.png?raw=true" width=50% height=50%>
</p>

<p align="center"> <a href='https://ko-fi.com/sniferl4bs' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' /></p>


## Caracteristicas


- Todos los componentes del laboratorio se ejecutan en contenedores Docker para garantizar un entorno aislado y seguro.
- La configuración del laboratorio se realiza mediante  Docker Compose, lo que facilita la personalización y la extensión del entorno según las necesidades del usuario y el desarrollo del mismo.
- Incluye varios servicios y aplicaciones vulnerables intencionalmente configurados para proporcionar casos de prueba realistas para pentesting.


## Desarrolladores

- [@Snifer](https://www.github.com/Snifer)


## Plan de desarrollo

###  Vulnerabilidades 

- Cryptographic Failures
- SQL Injection
- Insecure Design
- Security Misconfiguration
- XXE
- Vulnerable and Outdated Components 
- Identification and Authentication Failures
- Software and Data Integrity Failures 
- Security Logging and Monitoring Failures
- Server-Side Request Forgery
- API Vulnerable

### Adiciones 

- Panel de registro de flags.
- Interfaz de administración.



## Uso

Clona el repositorio de la siguiente manera.

```bash
git clone https://github.com/snifer/DinoSecL4b.git
```

Ingresa al directorio del proyecto. 

```Bash
cd DinoSecLab
```


Inicia el laboratorio con `docker-compose`

```Bash
docker-compose up -d
```

Con esto inicializaras los contenedores y se configurará de manera automatica el laboratorio. 

Puedes acceder al inicio del laboratorio desde https://localhost


## FAQ
\


## Screenshots

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Demo
\


## Support



## Contribuciones
¡Contribuciones son bienvenidas! 

Si encuentras algún problema o tienes sugerencias para mejorar el laboratorio, no dudes en abrir un issue o enviar una pull request.



## Documentación

[En progreso](https://sniferl4bs.com)


## Aviso Legal

Este laboratorio se proporciona con fines educativos y de entrenamiento en pentesting. No está destinado para uso en entornos de producción. 

Utiliza este laboratorio de manera ética y responsable.

## Licencia
Este proyecto está bajo la Licencia MIT. Consulta el archivo LICENSE para más detalles.

[MIT](https://choosealicense.com/licenses/mit/)

