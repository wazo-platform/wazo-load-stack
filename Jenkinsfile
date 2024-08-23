pipeline {
    agent any
    triggers {
        githubPush()
        pollSCM('H H * * *')
    }
    options {
        timestamps()
    }
    stages {
        stage('Changes to wlapi') {
            environment {
                VERSION = readFile('wazo_load_api/version').trim()
            }
            when { changeset "wazo_load_api/**" }
            steps {
                echo 'wlapi change detected'
                echo "New version: ${VERSION}"
                sh '''#!/bin/bash
                . wazo_load_pilot/docker-funcs
                registry-get-manifest wlapi $VERSION >> /dev/null
                if [ $? -eq "0" ]; then
                    echo "Version already available"
                    exit 0
                else
                    echo "building new docker image"
                fi
                '''
            }
        }
        stage('Changes to wlcli') {
            when { changeset "wazo_load_cli/**" }
            steps {
                echo 'wlcli change detected'
            }
        }
        stage('Changes to pilot') {
            when { changeset "wazo_load_pilot/**" }
            steps {
                echo 'pilot change detected'
            }
        }
    }
}
