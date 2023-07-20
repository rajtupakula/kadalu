#!/bin/bash

sudo docker login -u robot-preprod-deployer -p ov5t3dag8pqa1u5w dockerhub.cisco.com
#BUILD_DATE=`date +%y%m%d%H%M%S`

echo "Tag = $TAG"
sleep 120
if [ $BUILD_IMAGE == "KADALU_OPERATOR" ]
then 
 docker build -f kadalu_operator/Dockerfile -t dockerhub.cisco.com/robot-dockerprod/kadalu-operator:$TAG .
 if [[ "$?" -eq 0 ]]; then
    echo "Updating operator tag.."
    sed -i 's|###operator-tag###|'"$TAG"'|' helm/kadalu/charts/operator/templates/deployment.yaml
    echo "Pushing operator image...."
 	docker push dockerhub.cisco.com/robot-dockerprod/kadalu-operator:$TAG
    tar -cvf kadalu-helm-$TAG.tar -C helm kadalu/
    curl --noproxy cisco.com -i -X PUT -u robot-dev-deployer:qqyiwhc7ts6um8sw -v -C - -T kadalu-helm-$TAG.tar 'https://engci-maven.cisco.com/artifactory/robot-dev-snapshot/robot-base-vm/vgoogle/kadalu-helm-'${TAG}'.tar'
    #sed -i 's|'"$TAG"'|###operator-tag###|' helm/kadalu/charts/operator/templates/deployment.yaml    
 else
   exit 1
 fi
elif [ $BUILD_IMAGE == "KADALU_CSI_DRIVER" ]
then
 echo "docker build -f csi/Dockerfile -t dockerhub.cisco.com/robot-dockerprod/kadalu-csi-driver:$TAG ."
 docker build -f csi/Dockerfile -t dockerhub.cisco.com/robot-dockerprod/kadalu-csi-driver:$TAG .

 echo "Updating the csi tag before operator build"
 sed -i 's|###csi-tag###|'"$TAG"'|' templates/csi.yaml.j2

 echo "docker build -f kadalu_operator/Dockerfile -t dockerhub.cisco.com/robot-dockerprod/kadalu-operator:$TAG ."
 docker build -f kadalu_operator/Dockerfile -t dockerhub.cisco.com/robot-dockerprod/kadalu-operator:$TAG .
 if [[ "$?" -eq 0 ]]; then
    sed -i 's|###csi-tag###|'"$TAG"'|' helm/kadalu/charts/csi-nodeplugin/templates/daemonset.yaml
    sed -i 's|###operator-tag###|'"$TAG"'|' helm/kadalu/charts/operator/templates/deployment.yaml
    echo "Pushing kadalu-csi-driver ..."
 	docker push dockerhub.cisco.com/robot-dockerprod/kadalu-csi-driver:$TAG
    echo "Pushing kadalu-operator ..."
    docker push dockerhub.cisco.com/robot-dockerprod/kadalu-operator:$TAG
    tar -cvf kadalu-helm-$TAG.tar -C helm kadalu/
    echo "Successfully created kadalu-helm-$TAG.tar"
    curl --noproxy cisco.com -i -X PUT -u robot-dev-deployer:qqyiwhc7ts6um8sw -v -C - -T kadalu-helm-$TAG.tar 'https://engci-maven.cisco.com/artifactory/robot-dev-snapshot/robot-base-vm/vgoogle/kadalu-helm-'${TAG}'.tar'
    # sed -i 's|'"$TAG"'|###csi-tag###|' helm/kadalu/charts/csi-nodeplugin/templates/daemonset.yaml
    # sed -i 's|'"$TAG"'|###csi-tag###|' templates/csi.yaml.j2
    # sed -i 's|'"$TAG"'|###operator-tag###|' helm/kadalu/charts/operator/templates/deployment.yaml   
 else
    exit 1
 fi
fi
