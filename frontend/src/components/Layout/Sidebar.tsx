
import {
  Dashboard as DashboardIcon,
  AccountBalance,
  Receipt,
  Analytics,
  Business,
  Description,
  Notifications,
  Settings,
  CreditCard,  // Nouveau
  Upgrade,     // Nouveau
} from '@mui/icons-material';

const menuItems = [
  {
    title: 'Tableau de bord',
    path: '/dashboard',
    icon: <DashboardIcon />
  },
  {
    title: 'Plan comptable',
    path: '/plan-comptable',
    icon: <AccountBalance />
  },
  {
    title: 'Écritures',
    path: '/ecritures',
    icon: <Receipt />
  },
  {
    title: 'États financiers',
    path: '/etats-financiers',
    icon: <Analytics />
  },
  {
    title: 'Entités',
    path: '/entites',
    icon: <Business />
  },
  {
    title: 'Documents',
    path: '/documents',
    icon: <Description />
  },
  {
    title: 'Notifications',
    path: '/notifications',
    icon: <Notifications />
  },
  {
    title: 'Facturation',  // Nouveau
    path: '/billing',
    icon: <CreditCard />
  },
  {
    title: 'Plans d\'abonnement',  // Nouveau
    path: '/pricing',
    icon: <Upgrade />
  }
];