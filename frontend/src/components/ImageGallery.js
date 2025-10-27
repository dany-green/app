import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { inventoryAPI } from '@/lib/api';

export default function ImageGallery({ itemId, images = [], onImagesChange, canEdit = false }) {
  const [uploading, setUploading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const fileInputRef = useRef(null);
  const { toast } = useToast();

  const handleFileSelect = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);

    for (const file of files) {
      try {
        // Validate file type
        if (!file.type.startsWith('image/')) {
          toast({
            title: 'Ошибка',
            description: `${file.name} не является изображением`,
            variant: 'destructive',
          });
          continue;
        }

        // Validate file size (10MB)
        if (file.size > 10 * 1024 * 1024) {
          toast({
            title: 'Ошибка',
            description: `${file.name} слишком большой (макс. 10MB)`,
            variant: 'destructive',
          });
          continue;
        }

        // Upload
        const formData = new FormData();
        formData.append('file', file);

        const response = await inventoryAPI.uploadImage(itemId, formData);
        
        toast({
          title: 'Успешно',
          description: 'Изображение загружено',
        });

        // Update images list
        if (onImagesChange) {
          onImagesChange();
        }
      } catch (error) {
        toast({
          title: 'Ошибка',
          description: error.response?.data?.detail || `Не удалось загрузить ${file.name}`,
          variant: 'destructive',
        });
      }
    }

    setUploading(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleDelete = async (imageUrl) => {
    if (!window.confirm('Удалить это изображение?')) return;

    try {
      await inventoryAPI.deleteImage(itemId, imageUrl);
      toast({
        title: 'Успешно',
        description: 'Изображение удалено',
      });
      
      if (onImagesChange) {
        onImagesChange();
      }
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить изображение',
        variant: 'destructive',
      });
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!canEdit) return;

    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    // Create a synthetic event to reuse handleFileSelect
    const syntheticEvent = {
      target: {
        files: files,
      },
    };

    await handleFileSelect(syntheticEvent);
  };

  const getBackendUrl = () => {
    return process.env.REACT_APP_BACKEND_URL || '';
  };

  return (
    <div className="space-y-4">
      {/* Image Gallery */}
      {images && images.length > 0 && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {images.map((imageUrl, index) => (
            <div key={index} className="relative group">
              <Card className="overflow-hidden cursor-pointer hover:shadow-lg transition-shadow">
                <div className="aspect-square relative">
                  <img
                    src={`${getBackendUrl()}${imageUrl}`}
                    alt={`Фото ${index + 1}`}
                    className="w-full h-full object-cover"
                    onClick={() => setSelectedImage(`${getBackendUrl()}${imageUrl}`)}
                  />
                  {canEdit && (
                    <Button
                      size="sm"
                      variant="destructive"
                      className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(imageUrl);
                      }}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                  )}
                </div>
              </Card>
            </div>
          ))}
        </div>
      )}

      {/* Upload Area */}
      {canEdit && (
        <div
          className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={handleFileSelect}
            disabled={uploading}
          />
          
          {uploading ? (
            <div className="flex flex-col items-center">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600 mb-2" />
              <p className="text-sm text-gray-600">Загрузка...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <p className="text-sm font-medium text-gray-900 mb-1">
                Загрузить фотографии
              </p>
              <p className="text-xs text-gray-500">
                Нажмите или перетащите изображения сюда
              </p>
              <p className="text-xs text-gray-400 mt-1">
                JPG, PNG, WebP до 10MB
              </p>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {(!images || images.length === 0) && !canEdit && (
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
            <ImageIcon className="h-8 w-8 text-gray-400" />
          </div>
          <p className="text-sm text-gray-500">Нет фотографий</p>
        </div>
      )}

      {/* Image Preview Modal */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="relative max-w-4xl max-h-full">
            <Button
              size="sm"
              variant="outline"
              className="absolute top-4 right-4 bg-white"
              onClick={() => setSelectedImage(null)}
            >
              <X className="h-4 w-4" />
            </Button>
            <img
              src={selectedImage}
              alt="Preview"
              className="max-w-full max-h-[90vh] object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </div>
  );
}
