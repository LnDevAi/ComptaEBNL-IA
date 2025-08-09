#!/bin/bash

echo "🚀 DÉPLOIEMENT COMPTAEBNL-IA SUR AWS"
echo "===================================="
echo ""

# Configuration
STACK_NAME="ComptaEBNL-IA-Stack"
REGION="eu-west-1"  # Paris
KEY_PAIR_NAME=""    # À remplir

# Vérification des prérequis
echo "🔍 Vérification des prérequis AWS..."

# Vérification AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI n'est pas installé. Veuillez l'installer d'abord."
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html"
    exit 1
fi

# Vérification de la configuration AWS
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI n'est pas configuré. Exécutez 'aws configure' d'abord."
    exit 1
fi

echo "✅ AWS CLI configuré"

# Demande des paramètres
echo ""
echo "📝 Configuration du déploiement:"

if [ -z "$KEY_PAIR_NAME" ]; then
    echo "Paires de clés disponibles:"
    aws ec2 describe-key-pairs --region $REGION --query 'KeyPairs[].KeyName' --output table
    echo ""
    read -p "Nom de la paire de clés EC2 (pour SSH): " KEY_PAIR_NAME
fi

read -p "Région AWS [$REGION]: " INPUT_REGION
if [ ! -z "$INPUT_REGION" ]; then
    REGION=$INPUT_REGION
fi

read -p "Type d'instance EC2 [t3.medium]: " INSTANCE_TYPE
if [ -z "$INSTANCE_TYPE" ]; then
    INSTANCE_TYPE="t3.medium"
fi

echo ""
echo "🎯 Configuration choisie:"
echo "   Stack: $STACK_NAME"
echo "   Région: $REGION"
echo "   Paire de clés: $KEY_PAIR_NAME"
echo "   Type instance: $INSTANCE_TYPE"
echo ""

read -p "Continuer le déploiement? (y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "Déploiement annulé."
    exit 0
fi

echo ""
echo "🚀 Début du déploiement CloudFormation..."

# Déploiement CloudFormation
aws cloudformation deploy \
    --template-file cloudformation-template.yaml \
    --stack-name $STACK_NAME \
    --parameter-overrides \
        KeyPairName=$KEY_PAIR_NAME \
        InstanceType=$INSTANCE_TYPE \
    --capabilities CAPABILITY_IAM \
    --region $REGION

# Vérification du déploiement
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ DÉPLOIEMENT RÉUSSI !"
    echo "======================"
    
    # Récupération des outputs
    echo "📊 Informations de déploiement:"
    LOAD_BALANCER_DNS=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text)
    
    INSTANCE_IP=$(aws cloudformation describe-stacks \
        --stack-name $STACK_NAME \
        --region $REGION \
        --query 'Stacks[0].Outputs[?OutputKey==`InstancePublicIP`].OutputValue' \
        --output text)
    
    echo ""
    echo "🌐 ACCÈS À L'APPLICATION:"
    echo "   URL Principale: http://$LOAD_BALANCER_DNS"
    echo "   URL Directe: http://$INSTANCE_IP:9000"
    echo ""
    echo "🔧 ACCÈS TECHNIQUE:"
    echo "   SSH: ssh -i $KEY_PAIR_NAME.pem ec2-user@$INSTANCE_IP"
    echo "   Backend API: http://$INSTANCE_IP:5001"
    echo "   Frontend React: http://$INSTANCE_IP:3001"
    echo ""
    echo "📋 SERVICES DÉPLOYÉS:"
    echo "   ✅ Backend Flask avec API complète"
    echo "   ✅ Frontend React avec Material-UI"
    echo "   ✅ Page de démonstration unifiée"
    echo "   ✅ Plan comptable SYCEBNL (975+ comptes)"
    echo "   ✅ Intelligence artificielle intégrée"
    echo "   ✅ Load Balancer avec auto-scaling"
    echo ""
    echo "⏰ Attendre 5-10 minutes pour que tous les services soient opérationnels"
    echo ""
    echo "🎉 COMPTAEBNL-IA DÉPLOYÉ AVEC SUCCÈS SUR AWS !"
    
    # Sauvegarde des informations
    cat > deployment-info.txt << EOF
ComptaEBNL-IA - Informations de déploiement AWS
===============================================

Date de déploiement: $(date)
Région AWS: $REGION
Stack CloudFormation: $STACK_NAME

URLs d'accès:
- Application principale: http://$LOAD_BALANCER_DNS
- Accès direct: http://$INSTANCE_IP:9000
- Backend API: http://$INSTANCE_IP:5001
- Frontend React: http://$INSTANCE_IP:3001

Accès SSH:
ssh -i $KEY_PAIR_NAME.pem ec2-user@$INSTANCE_IP

Commandes utiles:
- Logs Docker: ssh ec2-user@$INSTANCE_IP "cd ComptaEBNL-IA/aws-deploy && docker-compose logs"
- Redémarrer: ssh ec2-user@$INSTANCE_IP "cd ComptaEBNL-IA/aws-deploy && docker-compose restart"
- Arrêter: aws cloudformation delete-stack --stack-name $STACK_NAME --region $REGION
EOF

    echo "📄 Informations sauvegardées dans: deployment-info.txt"
    
else
    echo ""
    echo "❌ ERREUR LORS DU DÉPLOIEMENT"
    echo "Vérifiez les logs CloudFormation dans la console AWS"
    exit 1
fi