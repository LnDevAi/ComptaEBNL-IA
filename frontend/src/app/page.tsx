'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { 
  BanknotesIcon, 
  ChartBarIcon, 
  DocumentTextIcon, 
  GlobeAltIcon,
  SparklesIcon,
  ShieldCheckIcon,
  UsersIcon,
  BuildingLibraryIcon
} from '@heroicons/react/24/outline'

const features = [
  {
    name: 'Conformité SYSCEBNL',
    description: 'Plan comptable officiel des entités à but non lucratif de l\'espace OHADA avec 1162 comptes intégrés',
    icon: BuildingLibraryIcon,
    color: 'text-primary-600',
    bgColor: 'bg-primary-50'
  },
  {
    name: 'Intelligence Artificielle',
    description: 'OCR automatique, génération d\'écritures, détection d\'anomalies et suggestions comptables',
    icon: SparklesIcon,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50'
  },
  {
    name: 'Multi-organisations',
    description: 'Gestion de plusieurs organisations avec isolement complet des données et rôles utilisateur',
    icon: UsersIcon,
    color: 'text-nonprofit-600',
    bgColor: 'bg-nonprofit-50'
  },
  {
    name: 'États Financiers OHADA',
    description: 'Bilan, compte de résultat, flux de trésorerie et annexes conformes aux normes OHADA',
    icon: DocumentTextIcon,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  },
  {
    name: 'Gestion EBNL Complète',
    description: 'Adhérents, cotisations, dons, projets, fonds affectés et reporting spécialisé EBNL',
    icon: BanknotesIcon,
    color: 'text-green-600',
    bgColor: 'bg-green-50'
  },
  {
    name: 'Sécurité Avancée',
    description: 'Chiffrement AES-256, audit trail complet, conformité RGPD et hébergement sécurisé',
    icon: ShieldCheckIcon,
    color: 'text-red-600',
    bgColor: 'bg-red-50'
  }
]

const ohadaCountries = [
  '🇧🇯 Bénin', '🇧🇫 Burkina Faso', '🇨🇲 Cameroun', '🇨🇫 Centrafrique', 
  '🇹🇩 Tchad', '🇰🇲 Comores', '🇨🇮 Côte d\'Ivoire', '🇨🇩 RD Congo',
  '🇬🇶 Guinée Équatoriale', '🇬🇦 Gabon', '🇬🇳 Guinée', '🇬🇼 Guinée-Bissau',
  '🇲🇱 Mali', '🇳🇪 Niger', '🇨🇬 Congo', '🇸🇳 Sénégal', '🇹🇬 Togo'
]

const stats = [
  { name: 'Pays OHADA couverts', value: '17', unit: '' },
  { name: 'Comptes SYSCEBNL', value: '1162', unit: '' },
  { name: 'Conformité OHADA', value: '100', unit: '%' },
  { name: 'Temps de traitement IA', value: '<5', unit: 'sec' }
]

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-white">
        <div className="absolute inset-y-0 h-full w-full" aria-hidden="true">
          <div className="relative h-full">
            <div className="absolute right-0 top-0 h-full w-1/2 ohada-gradient opacity-10" />
          </div>
        </div>
        
        <div className="relative mx-auto max-w-7xl px-6 py-24 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6 }}
            >
              <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-6xl">
                <span className="text-primary-600">ComptaOHADA-IA</span>
                <br />
                <span className="text-2xl sm:text-3xl text-gray-600 font-normal">
                  Plateforme de Comptabilité OHADA avec IA
                </span>
              </h1>
              
              <p className="mt-6 text-lg leading-8 text-gray-600">
                La première plateforme de comptabilité en ligne dédiée aux entités à but non lucratif 
                de l'espace OHADA avec intelligence artificielle intégrée selon les normes SYSCEBNL.
              </p>
              
              <div className="mt-10 flex items-center justify-center gap-x-6">
                <Link
                  href="/auth/register"
                  className="btn-primary px-8 py-3 text-base"
                >
                  Commencer gratuitement
                </Link>
                <Link
                  href="/demo"
                  className="btn-outline px-8 py-3 text-base"
                >
                  Voir la démo <ChartBarIcon className="ml-2 h-5 w-5" />
                </Link>
              </div>
              
              <div className="mt-8">
                <p className="text-sm text-gray-500">
                  ✅ Essai gratuit • ✅ Support OHADA • ✅ Conformité SYSCEBNL
                </p>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-primary-600 py-16">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Plateforme de référence pour l'espace OHADA
            </h2>
            <p className="mt-4 text-lg leading-8 text-primary-100">
              Développée spécifiquement pour répondre aux besoins des entités à but non lucratif 
              des 17 pays membres de l'OHADA
            </p>
          </div>
          
          <dl className="mx-auto mt-16 grid max-w-2xl grid-cols-1 gap-x-8 gap-y-10 text-white sm:mt-20 sm:grid-cols-2 sm:gap-y-16 lg:mx-0 lg:max-w-none lg:grid-cols-4">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="flex flex-col gap-y-3 border-l border-white/10 pl-6"
              >
                <dt className="text-sm leading-6 text-primary-100">{stat.name}</dt>
                <dd className="order-first text-3xl font-semibold tracking-tight">
                  {stat.value}{stat.unit}
                </dd>
              </motion.div>
            ))}
          </dl>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-24 sm:py-32 bg-gray-50">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-base font-semibold leading-7 text-primary-600">
              Fonctionnalités complètes
            </h2>
            <p className="mt-2 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Tout ce dont vous avez besoin pour votre comptabilité EBNL
            </p>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Une solution complète et moderne adaptée aux spécificités des entités 
              à but non lucratif de l'espace OHADA
            </p>
          </div>
          
          <div className="mx-auto mt-16 max-w-2xl sm:mt-20 lg:mt-24 lg:max-w-none">
            <dl className="grid max-w-xl grid-cols-1 gap-x-8 gap-y-16 lg:max-w-none lg:grid-cols-3">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="flex flex-col"
                >
                  <dt className="text-base font-semibold leading-7 text-gray-900">
                    <div className={`mb-6 flex h-10 w-10 items-center justify-center rounded-lg ${feature.bgColor}`}>
                      <feature.icon className={`h-6 w-6 ${feature.color}`} aria-hidden="true" />
                    </div>
                    {feature.name}
                  </dt>
                  <dd className="mt-1 flex flex-auto flex-col text-base leading-7 text-gray-600">
                    <p className="flex-auto">{feature.description}</p>
                  </dd>
                </motion.div>
              ))}
            </dl>
          </div>
        </div>
      </div>

      {/* OHADA Countries Section */}
      <div className="py-24 sm:py-32 bg-white">
        <div className="mx-auto max-w-7xl px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <GlobeAltIcon className="mx-auto h-12 w-12 text-nonprofit-600" />
            <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900 sm:text-4xl">
              Espace OHADA Couvert
            </h2>
            <p className="mt-6 text-lg leading-8 text-gray-600">
              Support complet pour les 17 pays membres de l'Organisation pour l'Harmonisation 
              en Afrique du Droit des Affaires
            </p>
          </div>
          
          <div className="mx-auto mt-16 grid max-w-4xl grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
            {ohadaCountries.map((country, index) => (
              <motion.div
                key={country}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="flex items-center justify-center rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm font-medium text-gray-900 hover:bg-gray-50 transition-colors"
              >
                {country}
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-600">
        <div className="px-6 py-24 sm:px-6 sm:py-32 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
              Prêt à moderniser votre comptabilité ?
            </h2>
            <p className="mx-auto mt-6 max-w-xl text-lg leading-8 text-primary-100">
              Rejoignez les organisations qui ont choisi ComptaOHADA-IA pour 
              leur gestion comptable conforme aux normes OHADA et SYSCEBNL.
            </p>
            <div className="mt-10 flex items-center justify-center gap-x-6">
              <Link
                href="/auth/register"
                className="rounded-md bg-white px-8 py-3 text-base font-semibold text-primary-600 shadow-sm hover:bg-primary-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white transition-colors"
              >
                Commencer maintenant
              </Link>
              <Link
                href="/contact"
                className="text-base font-semibold leading-6 text-white hover:text-primary-100 transition-colors"
              >
                Nous contacter <span aria-hidden="true">→</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}