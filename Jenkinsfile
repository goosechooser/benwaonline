pipeline {
    agent any
    stages {
        stage('Build image') {
            steps {
                sh 'find . -name "*.pyc" -delete'
                sh 'mkdir work_dir'
                sh 'docker-compose build testing'
            }
        }

        stage('Test image') {
            steps {
                sh 'docker run --name memcached -d -p 11212:11212 memcached -p 11212'
                sh 'docker-compose run testing'

                step([$class: 'CoberturaPublisher', autoUpdateHealth: false,
                autoUpdateStability: false, coberturaReportFile: './work_dir/coverage.xml',
                failNoReports: false, failUnhealthy: false, failUnstable: false,
                maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
            }
        }

    }
    post {
        always {
            sh 'docker rm --force memcached'
            sh 'rm -rf work_dir'
        }
        success {
            echo 'I succeeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}
