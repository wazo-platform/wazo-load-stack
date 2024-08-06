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
            when { changeset "wazo_load_api/**" }
            steps {
                echo 'wlapi change detected'
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
