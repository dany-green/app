import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Building2, FolderKanban, Package, Users, LogOut, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export default function Layout({ children }) {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Проекты', href: '/', icon: FolderKanban },
    { name: 'Инвентарь', href: '/inventory', icon: Package },
  ];

  if (isAdmin()) {
    navigation.push(
      { name: 'Пользователи', href: '/users', icon: Users },
      { name: 'Логи', href: '/logs', icon: Activity }
    );
  }

  const getInitials = (name) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'Администратор':
        return 'bg-red-500';
      case 'Ведущий декоратор':
        return 'bg-blue-500';
      case 'Куратор студии':
        return 'bg-green-500';
      case 'Флорист':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center px-4">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 mr-8">
            <Building2 className="h-6 w-6 text-primary" />
            <span className="font-bold text-xl">SLS1</span>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center space-x-2 flex-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <Link key={item.name} to={item.href}>
                  <Button
                    variant={isActive ? 'secondary' : 'ghost'}
                    className={cn(isActive && 'bg-secondary')}
                    data-testid={`nav-${item.name.toLowerCase()}`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Button>
                </Link>
              );
            })}
          </nav>

          {/* User Menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="relative h-10 w-10 rounded-full" data-testid="user-menu-trigger">
                <Avatar className="h-10 w-10">
                  <AvatarFallback className={cn('text-white', getRoleBadgeColor(user?.role))}>
                    {user ? getInitials(user.name) : 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent className="w-56" align="end" forceMount>
              <DropdownMenuLabel className="font-normal">
                <div className="flex flex-col space-y-1">
                  <p className="text-sm font-medium leading-none">{user?.name}</p>
                  <p className="text-xs leading-none text-muted-foreground">{user?.email}</p>
                  <p className="text-xs leading-none text-muted-foreground mt-1">
                    <span className={cn('inline-block w-2 h-2 rounded-full mr-1', getRoleBadgeColor(user?.role))} />
                    {user?.role}
                  </p>
                </div>
              </DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={handleLogout} data-testid="logout-button">
                <LogOut className="mr-2 h-4 w-4" />
                <span>Выход</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </header>

      {/* Main Content */}
      <main className="container py-6 px-4">
        {children}
      </main>
    </div>
  );
}
