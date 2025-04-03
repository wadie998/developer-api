library identifier: 'jenkins@master',
        retriever: modernSCM([  $class: 'GitSCMSource',
                                credentialsId: 'bitbucket-credentials',
                                remote: 'https://bitbucket.org/kaoun/jenkins.git'
                            ])

genericPythonBuildDeploy    dockerImage: 'kaoun/django-developers-api',
                                extraMailingList: 'devops@flouci.com',
                                deploy_name: 'django-developers-api',
                                deploy_dev: true,
                                deploy_sta: true
