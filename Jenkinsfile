pipeline {
    agent any
    stages {
        stage('Build image') {
            steps {
                // sh 'docker-compose -f docker-compose.yml build testing'
                sh 'docker build -t benwaonline:testing --target testing .'
            }
        }

        stage('Test image') {
            steps {
                sh 'docker run --name memcached -d -p 11212:11212 memcached -p 11212'
                sh 'docker-compose -f docker-compose.yml run testing'
                sh 'docker cp testing:/usr/src/app/coverage.xml .'

                step([$class: 'CoberturaPublisher', autoUpdateHealth: false,
                autoUpdateStability: false, coberturaReportFile: 'coverage.xml',
                failNoReports: false, failUnhealthy: false, failUnstable: false,
                maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
            }
        }

    }
    post {
        always {
            sh 'docker rm --force memcached'
            cleanWs()
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
// node {
//     def app

//     stage('Clone repository') {
//         checkout scm
//     }

//     stage('Build image') {
//         // sh 'docker-compose -f docker-compose.yml build testing'
//         sh 'docker build -t benwaonline:testing --target testing .'
//     }
//     try {
//         stage('Test image') {
//             sh 'docker run --name memcached -d -p 11212:11212 memcached -p 11212'
//             sh 'docker-compose -f docker-compose.yml run testing'
//             sh 'docker cp testing:/usr/src/app/coverage.xml .'

//             step([$class: 'CoberturaPublisher', autoUpdateHealth: false,
//             autoUpdateStability: false, coberturaReportFile: 'coverage.xml',
//             failNoReports: false, failUnhealthy: false, failUnstable: false,
//             maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
//         }
//         echo 'Tests successful'
//     } catch (e) {
//         echo 'Tests failed'
//         throw e
//     } finally {
//     }
//     stage('Clean up'){
//         cleanWs()
//         sh 'docker rm --force memcached'
//     }
// }