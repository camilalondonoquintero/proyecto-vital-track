Documentación General del Sistema VitalTrack
Descripción del sistema

VitalTrack es una aplicación web desarrollada con Flask que permite a los usuarios llevar un control de hábitos saludables y realizar seguimiento a su progreso diario. La plataforma está orientada a la organización personal del bienestar, permitiendo registrar actividades, medir avances y visualizar estadísticas relacionadas con los hábitos creados.

El sistema funciona mediante renderizado del lado del servidor utilizando Jinja2 y almacena la información en una base de datos SQLite. La estructura del proyecto está organizada por capas para separar la lógica de negocio, el manejo de rutas, los modelos y las utilidades auxiliares.

Objetivos principales

El propósito principal de VitalTrack es ofrecer una herramienta sencilla para:

Registrar e iniciar sesión de usuarios.
Gestionar perfiles personales.
Crear y administrar hábitos saludables.
Registrar avances diarios asociados a cada hábito.
Mostrar métricas básicas de progreso y cumplimiento.
Presentar consejos saludables de manera aleatoria dentro del panel principal.
Organización del proyecto

La aplicación se encuentra dividida en diferentes módulos para facilitar su mantenimiento y escalabilidad.

main.py funciona como punto de inicio de la aplicación.
app/__init__.py configura Flask, inicializa SQLAlchemy y registra los blueprints.
app/controllers/web.py contiene las rutas web y el manejo de sesiones.
app/services/ agrupa la lógica de negocio relacionada con hábitos y usuarios.
app/models/ contiene las entidades y modelos de base de datos.
app/utils/ incluye validaciones y funciones auxiliares de autenticación.
app/templates/ almacena las vistas HTML desarrolladas con Jinja2.
app/static/css/styles.css contiene los estilos visuales.
tests/test_app.py incluye pruebas unitarias y de integración.
Tecnologías utilizadas

El sistema fue desarrollado utilizando las siguientes herramientas y librerías:

Flask 3.0.3
Flask-SQLAlchemy 3.1.1
Requests 2.32.3
Pytest 8.3.5
SQLite como motor de base de datos

La base de datos principal se almacena en el archivo:

healthy_habits.db

Modelo de datos
Usuario (User)

Representa a cada persona registrada dentro del sistema.

Información almacenada
Nombre completo
Correo electrónico
Contraseña cifrada
Edad
Objetivo de bienestar
Fechas de creación y actualización
Funcionalidades principales

El modelo permite:

Cifrar contraseñas.
Verificar credenciales.
Obtener el primer nombre del usuario.
Contar la cantidad de hábitos registrados.

Cada usuario puede tener múltiples hábitos asociados.

Hábito (Habit)

Representa una actividad o meta saludable definida por el usuario.

Información almacenada
Título
Descripción
Categoría
Tipo de métrica
Valor objetivo
Unidad de medida
Frecuencia
Estado activo
Usuario propietario
Funcionalidades principales

El sistema permite:

Calcular porcentaje de cumplimiento.
Obtener progreso diario.
Calcular rachas actuales.
Calcular promedios semanales.
Consultar registros recientes.

Cada hábito pertenece a un único usuario y puede contener múltiples registros.

Registro de hábito (HabitLog)

Corresponde a los avances diarios registrados para un hábito específico.

Información almacenada
Fecha del registro
Valor registrado
Nota opcional
Hábito asociado

Cada registro pertenece únicamente a un hábito.

Tipos de seguimiento

VitalTrack maneja distintos tipos de métricas para evaluar hábitos:

quantity: calcula el progreso según la cantidad registrada frente a la meta establecida.
duration: similar a quantity, pero pensado para tiempos en minutos u horas.
boolean: considera el hábito cumplido cuando el valor registrado es igual o superior a 1.
Funcionamiento general del sistema

El flujo básico de uso es el siguiente:

El usuario ingresa a la página principal.
Puede registrarse o iniciar sesión.
La sesión almacena el identificador del usuario autenticado.
El sistema carga automáticamente la información del usuario actual.
Desde el dashboard se pueden:
visualizar métricas,
consultar tips saludables,
crear hábitos,
registrar avances,
editar información,
eliminar hábitos o registros.
Rutas principales

La aplicación dispone de rutas para autenticación, gestión de usuarios y administración de hábitos.

Autenticación
/ → página principal.
/auth/register → registro de usuarios.
/auth/login → inicio de sesión.
/auth/logout → cierre de sesión.
Perfil de usuario
/dashboard → panel principal.
/profile → perfil del usuario.
/users/<user_id> → acceso controlado al perfil.
/profile/update → actualización de información personal.
/profile/delete → eliminación de cuenta.
Hábitos y registros
/habits/create → creación de hábitos.
/habits/<habit_id>/update → edición de hábitos.
/habits/<habit_id>/delete → eliminación de hábitos.
/habits/<habit_id>/logs/create → creación de registros.
/logs/<log_id>/delete → eliminación de registros.
Validaciones y reglas de negocio

El sistema aplica diversas validaciones para garantizar la integridad de la información:

El correo debe tener un formato válido.
La edad debe ser un número entero positivo.
El valor objetivo debe ser numérico y mayor o igual a 1.
Los avances registrados no pueden ser negativos.
La contraseña debe tener mínimo seis caracteres.
La confirmación de contraseña debe coincidir.
Cada usuario solo puede modificar sus propios hábitos y registros.
Si un correo ya existe, se captura la excepción correspondiente y se informa al usuario.
Interfaz del sistema

La interfaz está desarrollada completamente con renderizado del lado del servidor utilizando HTML y Jinja2.

Vistas principales
base.html → estructura general y navegación.
home.html → pantalla de inicio, login y registro.
dashboard.html → panel principal y gestión de hábitos.
user_detail.html → edición de perfil y eliminación de cuenta.

El proyecto no utiliza arquitectura SPA ni API pública REST; toda la interacción se realiza mediante formularios tradicionales.

Servicios auxiliares

El sistema incluye algunos servicios complementarios:

Tips saludables

tips_service.py genera consejos saludables aleatorios desde una lista local.

Servicio de recetas

recipe_api_service.py realiza consultas a TheMealDB para obtener recetas y normalizar datos, aunque actualmente no está integrado en la interfaz.

Configuración adicional

config/settings.py contiene variables relacionadas con una futura integración de ejercicios físicos mediante API externa.

Variables de configuración

La aplicación utiliza variables de entorno y configuración como:

SECRET_KEY
DATABASE_URL
EXERCISE_API_BASE_URL
EXERCISE_DEFAULT_LANGUAGE
EXERCISE_API_TIMEOUT
Estado actual del proyecto

Según la revisión realizada el 29 de abril de 2026, el proyecto presenta algunos aspectos pendientes:

Existe una inconsistencia porque ciertos archivos importan exercise_api_service.py, pero dicho archivo no está presente en el proyecto.
Esto provoca errores al importar el paquete app.services.
La frecuencia semanal actualmente solo se almacena visualmente; los cálculos internos siguen funcionando de manera diaria.
Hay métodos similares para resúmenes (dashboard_summary() y user_dashboard_summary()), pero únicamente uno es utilizado por la interfaz.
Ejecución del proyecto

El sistema puede ejecutarse mediante scripts preparados para Windows PowerShell:

run_app.ps1 → inicia la aplicación.
run_tests.ps1 → ejecuta las pruebas automatizadas con Pytest.
