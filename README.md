# DISCORD BOT

Este bot registra todos los cambios de estado de todos los usuarios de un servidor de Discord y una vez al día envia a
un grupo dentro del servidor los datos de las horas conectadas de cada usuario.

También se conecta a un calendario de Google para mirar todos los eventos que existen, lo revisa dos veces al día. Coge 
esos eventos y cada 15 minutos mira los eventos que hay cerca para avisar en el canal que corresponda de Discord. Se 
puede configurar metiendo más canales y reconocimiento de eventos.


## Crear un bot en Discord

1. Ve a Discord Developer Portal. (https://discord.com/developers/applications)
2. Haz clic en “New Application”, ponle un nombre a tu bot y crea la aplicación. 
3. En el menú de la izquierda, selecciona “Bot” y haz clic en “Add Bot”. 
4. Copia el token de tu bot, lo necesitarás para ponerlo en .env. 
5. Ve a la sección “OAuth2”, luego a “URL Generator”. 
6. En “SCOPES”, selecciona bot y en “BOT PERMISSIONS”, selecciona los permisos que desees (por ejemplo, Send Messages). 
7. Copia la URL generada, ábrela en el navegador y selecciona el servidor al que deseas invitar el bot.

En .env tienes que meter el token de Discord los canales de Discord de esta forma.
TOKEN_BOT_DISCORD=<token>
DISCORD_CHANNEL={"GENERAL": <channel_id>, "CONTROL": <channel_id>}

##  Conectarse a Google calendar

1. Ve a Google Cloud Console. (https://cloud.google.com/gcp/)
2. Crea un proyecto nuevo o selecciona uno existente.
3. Habilita la Google Calendar API:
•	En el menú de la izquierda, ve a “API & Services” > “Library”.
•	Busca “Google Calendar API” y haz clic en “Enable”.
4. Configura las credenciales:
•	Ve a “Credentials” en el menú de la izquierda.
•	Haz clic en “Create Credentials” y selecciona OAuth 2.0 Client ID.
•	Si es tu primera vez, tendrás que configurar la pantalla de consentimiento (puedes poner datos básicos para pruebas).
•	Después, selecciona “Desktop App” como el tipo de aplicación.
•	Descarga el archivo credentials.json.

En .env tienes que meter los datos de acceso al calendario, json_credentials es el json que viene dentro del fichero
de credenciales que obtienes en Google Cloud Console
CALENDAR_SCOPES=https://www.googleapis.com/auth/calendar
CALENDAR_ID=<calendar_id>
CALENDAR_CREDENTIALS=<json_credentials>
