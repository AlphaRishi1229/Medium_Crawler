#!/bin/bash

echo "------------------------------------------------------------------------"
echo "Starting Server Locally."
echo "------------------------------------------------------------------------"
CAN_RUN="yes"
ACTION="$1"
BUILD="$2"
NOCACHE="$3"
# Available SHARED SERVICES Are: ["postgresql", "redis"]
APP_NAME="crawler-medium"
SHARED_SERVICES=("postgresql", "redis")
echo "Repository Name: $APP_NAME"
echo "List Of Shared Services: ${SHARED_SERVICES[@]}"
echo ""
echo ""

# -----------------------------------------------------------------------------
# DO NOT MAKE CHANGES BELOW.
# -----------------------------------------------------------------------------
echo "------------------------------------------------------------------------"
echo "Checking If 'docker-compose.yml' Exist."
echo "------------------------------------------------------------------------"
COMPOSE_YML_EXISTS=$([ -f "docker-compose.yml" ] && echo "yes")
if [ "$COMPOSE_YML_EXISTS" != "yes" ]; then
    echo "Error: We Could Not Find 'docker-compose.yml' In '$APP_NAME'."
    exit 1
else
    echo "Found 'docker-compose.yml' In '$APP_NAME'."
fi
echo ""
echo ""

if [ "$ACTION" == "start" ]; then
    echo "------------------------------------------------------------------------"
    echo "Starting Services At '$APP_NAME'."
    echo "------------------------------------------------------------------------"
    if [ "$CAN_RUN" = "yes" ]; then
        if [ "$BUILD" = "build" ]; then
            if [ "$NOCACHE" = "nocache" ]; then
                docker-compose build --no-cache
                docker-compose up
            else
                docker-compose up --build
            fi
        else
            docker-compose up
        fi
    else
        echo "Error: We Could Not Run Shared Services."
    fi

elif [ "$ACTION" = "stop" ]; then
    echo "--------------------------------------------------------------------"
    echo "Stoping Services At '$APP_NAME'"
    echo "--------------------------------------------------------------------"
    docker-compose down
    echo ""
    echo ""

elif [ "$ACTION" = "status" ]; then
    echo "--------------------------------------------------------------------"
    echo "Status Of Services At '$APP_NAME'"
    echo "--------------------------------------------------------------------"
    RUNNING_CONT="$(docker ps)"
    if echo "$RUNNING_CONT" | grep -q "crawler-medium"; then
        echo "crawler-medium: Up"
    else
        echo "crawler-medium: Down"
    fi

else
    echo "Error: Invalid Command, Provide 'start', 'stop' or 'status' As Arguement."
fi
