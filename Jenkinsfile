library identifier: 'jenkins@master',
        retriever: modernSCM([  $class: 'GitSCMSource',
                                credentialsId: 'bitbucket-credentials',
                                remote: 'https://bitbucket.org/kaoun/jenkins.git'
                            ])

genericPythonBuildDeploy    dockerImage: 'kaoun/django-template-app',
                                extraMailingList: 'devops@flouci.com',
                                deploy_name: 'sms',
                                deploy_dev: true,
                                deploy_sta: true
