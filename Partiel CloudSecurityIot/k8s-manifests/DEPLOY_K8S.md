# 🚀 Guide de Déploiement K8s (MicroK8s + Multipass)

Ce guide utilise les commandes de votre cours pour déployer notre projet IoT Cloud Security.

## 1. Préparation de la VM

```bash
# Lancer et entrer dans la VM
multipass primary shell

# Installation de MicroK8s
sudo snap install --classic microk8s
sudo usermod -a -G microk8s $USER
newgrp microk8s

# Attendre que tout soit prêt
microk8s status --wait-ready

# Activer les modules nécessaires
sudo microk8s enable dns ingress storage registry
```

## 2. Alias et Docker

```bash
# Créer l'alias pour kubectl (comme en cours)
alias kubectl='microk8s kubectl'

# Installer Docker pour gérer nos images
sudo apt install docker.io
```

## 3. Déploiement du Projet

_Note : Assurez-vous d'avoir transféré le dossier `k8s-manifests` dans la VM._

```bash
# 1. Configuration et Secrets
kubectl apply -f k8s-manifests/config/

# 2. Bases de données et Messaging
kubectl apply -f k8s-manifests/databases/
kubectl apply -f k8s-manifests/messaging/

# 3. Microservices (3 réplicas chacun)
kubectl apply -f k8s-manifests/services/

# 4. Ingress (Le remplaçant de Nginx)
kubectl apply -f k8s-manifests/ingress/

# 5. Monitoring
kubectl apply -f k8s-manifests/monitoring/
```

## 4. Vérification (Commandes utiles)

```bash
# Voir si tout tourne (Pods, Services, Ingress)
kubectl get all -o wide

# Vérifier les 3 instances de chaque service
kubectl get pods

# Voir les logs en cas de problème
kubectl logs <nom-du-pod> --tail=20

# Décrire un service pour voir son IP interne
kubectl describe svc auth-service
```

## 5. Accès au Dashboard

1. Récupérez l'IP de votre VM : `multipass info primary`.
2. Modifiez votre fichier `hosts` Windows pour pointer `iot-cloud.local` vers cette IP.
3. Testez l'accès : `http://iot-cloud.local/auth/health`
