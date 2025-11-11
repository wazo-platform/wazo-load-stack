pipeline {
  agent {
    label 'general-debian12-medium'
  }
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
        IMAGE = 'wazoplatform/wlapi'
      }
      when { changeset "wazo_load_api/**" }
        steps {
          withCredentials([usernamePassword(
            credentialsId: 'docker-wazocommunity-user-password',
            passwordVariable: 'DOCKER_PASSWORD',
            usernameVariable: 'DOCKER_USERNAME'
          )]) {
            echo 'wlapi change detected'
            echo "New version: ${VERSION}"
            sh '''#!/bin/bash
            set -x
            . wazo_load_pilot/docker-funcs
            docker manifest inspect $IMAGE:$VERSION >> /dev/null
            if [ $? -eq "0" ]; then
                echo "Version already available"
                exit 0
            else
                set -e
                echo "building new docker image"
                git submodule update --init --recursive
                pushd wazo_load_api
                make build-dockerfile
                make build-api
                popd
                docker tag $IMAGE:$VERSION $IMAGE:$VERSION
                docker login -u ${DOCKER_USERNAME} -p "${DOCKER_PASSWORD}"
                docker push $IMAGE:$VERSION
            fi
            '''
          }
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
