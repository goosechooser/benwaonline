node {
    def app

    stage('Clone repository') {
        checkout scm
    }

    stage('Build image') {
        sh 'docker-compose -f docker-compose.yml build testing'
    }
    try {
        stage('Test image') {
            sh 'docker run --name memcached -d -p 11212:11212 memcached -p 11212'
            sh 'docker-compose -f docker-compose.yml run testing'
            sh 'docker cp testing:/usr/src/app/coverage.xml .'

            step([$class: 'CoberturaPublisher', autoUpdateHealth: false,
            autoUpdateStability: false, coberturaReportFile: 'coverage.xml',
            failNoReports: false, failUnhealthy: false, failUnstable: false,
            maxNumberOfBuilds: 0, onlyStable: false, sourceEncoding: 'ASCII', zoomCoverageChart: false])
        }
        echo 'Tests successful'
    } catch (e) {
        echo 'Tests failed'
        throw e
    } finally {
        sh 'docker rm --force memcached'
    }
}