import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../hooks/use-toast';

const UserProfile = ({ onClose }) => {
  const { user, logout, updateProfile } = useAuth();
  const { toast } = useToast();
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    dailyGoal: user?.dailyGoal || 5,
    difficulty: user?.difficulty || 'medium',
    preferredCategories: user?.preferredCategories || []
  });

  const handleSave = async () => {
    setLoading(true);
    try {
      await updateProfile(formData);
      setEditing(false);
      toast({
        title: "Profile Updated",
        description: "Your preferences have been saved successfully.",
      });
    } catch (error) {
      console.error('Profile update error:', error);
      toast({
        title: "Update Failed",
        description: "Failed to update profile. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    onClose();
    toast({
      title: "Signed Out",
      description: "You have been signed out successfully.",
    });
  };

  if (!user) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>👤 Your Profile</span>
            <Button variant="outline" onClick={onClose}>
              ✕
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Account Info */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Account Information</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <div className="text-gray-900">{user.email}</div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Subscription
                </label>
                <Badge variant="outline" className="capitalize">
                  {user.subscriptionType}
                </Badge>
              </div>
            </div>
          </div>

          {/* Profile Settings */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Learning Preferences</h3>
              {!editing && (
                <Button variant="outline" onClick={() => setEditing(true)}>
                  Edit
                </Button>
              )}
            </div>

            {editing ? (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name
                  </label>
                  <Input
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Daily Goal (mitzvot per day)
                  </label>
                  <Select 
                    value={formData.dailyGoal.toString()} 
                    onValueChange={(value) => setFormData({ ...formData, dailyGoal: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="3">3 mitzvot/day (Light)</SelectItem>
                      <SelectItem value="5">5 mitzvot/day (Moderate)</SelectItem>
                      <SelectItem value="10">10 mitzvot/day (Intensive)</SelectItem>
                      <SelectItem value="20">20 mitzvot/day (Expert)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Learning Difficulty
                  </label>
                  <Select 
                    value={formData.difficulty} 
                    onValueChange={(value) => setFormData({ ...formData, difficulty: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="easy">Easy - Basic concepts</SelectItem>
                      <SelectItem value="medium">Medium - Balanced learning</SelectItem>
                      <SelectItem value="hard">Hard - Advanced study</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="flex gap-2">
                  <Button onClick={handleSave} disabled={loading}>
                    {loading ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button variant="outline" onClick={() => setEditing(false)}>
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <div className="text-gray-900">{user.name}</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Daily Goal
                  </label>
                  <div className="text-gray-900">{user.dailyGoal} mitzvot/day</div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <Badge variant="outline" className="capitalize">
                    {user.difficulty}
                  </Badge>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Study Time
                  </label>
                  <div className="text-gray-900">{user.totalStudyTime || 0} minutes</div>
                </div>
              </div>
            )}
          </div>

          {/* Member Since */}
          <div className="space-y-2">
            <h3 className="text-lg font-semibold">Account Details</h3>
            <div className="text-gray-600">
              Member since {new Date(user.createdAt).toLocaleDateString()}
            </div>
          </div>

          {/* Actions */}
          <div className="border-t pt-4">
            <Button variant="destructive" onClick={handleLogout} className="w-full">
              Sign Out
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default UserProfile;