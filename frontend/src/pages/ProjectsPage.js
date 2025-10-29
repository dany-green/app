import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectsAPI } from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Loader2, Calendar, User, FolderKanban } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function ProjectsPage() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    title: '',
    lead_decorator: '',
    project_date: '',
  });

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const data = await projectsAPI.getAll();
      setProjects(data);
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить проекты',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      // Преобразовать дату в ISO формат
      const projectData = {
        ...formData,
        project_date: new Date(formData.project_date).toISOString(),
      };
      await projectsAPI.create(projectData);
      toast({ title: 'Проект создан' });
      setDialogOpen(false);
      resetForm();
      loadProjects();
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.response?.data?.detail || 'Ошибка создания проекта',
        variant: 'destructive',
      });
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      lead_decorator: '',
      project_date: '',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Создан':
        return 'bg-blue-500';
      case 'На согласовании':
        return 'bg-yellow-500';
      case 'Согласован':
        return 'bg-green-500';
      case 'Сбор проекта':
        return 'bg-purple-500';
      case 'Монтаж':
        return 'bg-orange-500';
      case 'Демонтаж':
        return 'bg-red-500';
      case 'Разбор':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight" data-testid="projects-page-title">Проекты</h1>
          <p className="text-muted-foreground">Управление проектами и мероприятиями</p>
        </div>
        <Button onClick={() => navigate('/projects/new')} data-testid="create-project-button">
          <Plus className="mr-2 h-4 w-4" />
          Создать проект
        </Button>
      </div>

      {projects.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <FolderKanban className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Нет проектов</h3>
            <p className="text-sm text-muted-foreground mb-4">Начните с создания вашего первого проекта</p>
            <Button onClick={() => navigate('/projects/new')}>
              <Plus className="mr-2 h-4 w-4" />
              Создать проект
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Card
              key={project.id}
              className="cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => navigate(`/projects/${project.id}`)}
              data-testid={`project-card-${project.id}`}
            >
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg" data-testid={`project-title-${project.id}`}>{project.title}</CardTitle>
                    <CardDescription className="mt-2 flex items-center text-sm">
                      <User className="h-3 w-3 mr-1" />
                      {project.lead_decorator}
                    </CardDescription>
                  </div>
                  <Badge className={getStatusColor(project.status)} data-testid={`project-status-${project.id}`}>
                    {project.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm text-muted-foreground">
                  <Calendar className="h-4 w-4 mr-2" />
                  {format(new Date(project.project_date), 'dd MMMM yyyy', { locale: ru })}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
