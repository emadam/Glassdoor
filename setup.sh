mkdir -p ~/.streamlit/

echo "\
[general]\n\
email = \"${HEROKU_EMAIL_ADDRESS}\"\n\
" > ~/.streamlit/credentials.toml

echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = $PORT\n\
[theme]
base='light'
primaryColor='#00ABE1'
backgroundColor='#FFFFFF'
secondaryBackgroundColor='#D3D3D3'
textColor='#161F6D'
font='sans serif'
" > ~/.streamlit/config.toml
