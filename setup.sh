#!/bin/bash
# TODO: Validate input and test on each build that it still works (prevents support cases)

if [ ! -f ".env" ]; then
   read -p "What is your Signalwire space: " sig_space;
   read -p "What is your Signalwire project ID: " proj_id;
   read -p "What is your Signalwire REST API token: " api_token;
   read -p "What is your Signalwire Sip Endpoint username: " sip_endpiont_username;
   read -p "What is your Signalwire Sip Endpoint password: " sip_endpiont_password;
   read -p "What is your Signalwire Sip URI: " sip_endpiont_uri;
   read -p "Signalwire number to make calls: " sig_number;
   read -p "Editor (nano, vim, emacs): " visual;

   # Remove domain, if attached to signalwire space
   sig_space=$( echo "${sig_space}" | cut -d \. -f1 )

   URL="https://${sig_space}.signalwire.com/api/laml/2010-04-01/Accounts -u ${proj_id}:${api_token}"
   response_code=$(curl -s -o /dev/null -I -w "%{http_code}" $URL )
   if [[ $response_code  -eq 200 ]]; then
      echo "SIGNALWIRE_SPACE=$sig_space" > .env
      echo "PROJECT_ID=$proj_id" >> .env
      echo "REST_API_TOKEN=$api_token" >> .env
      echo "SIGNALWIRE_SIP_ENDPOINT_USERNAME=$sip_endpiont_username" >> .env
      echo "SIGNALWIRE_SIP_ENDPOINT_PASSWORD=$sip_endpiont_password" >> .env
      echo "SIGNALWIRE_SIP_ENDPOINT_URI=$sip_endpiont_uri" >> .env
      echo "SIGNALWIRE_NUMBER=$sig_number" >> .env
      echo "VISUAL=$visual" >> .env
      echo "setup successful"
   elif [[ $response_code -eq 404 ]]; then
      echo "Make sure you entered correct space URL"
   elif [[ $response_code -eq 401 ]]; then
      echo "Make sure you entered correct project ID and REST API token"
   else
      echo  "Setup failed please try again"
   fi
else
   # This can be changed once .env file validation is happening
   # Search for .signalwire.com and remove if exists
   #sed -i~ 's/\.signalwire.com//g' .env

   echo "Setup .env file already exists"
fi