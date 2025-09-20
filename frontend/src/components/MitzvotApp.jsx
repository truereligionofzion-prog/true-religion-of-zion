import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, BookOpen, Tag, Info, Loader, User, UserPlus, LogIn } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from '../hooks/use-toast';
import { Toaster } from './ui/toaster';
import apiService from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import UserProfile from './UserProfile';

const MitzvotApp = () => {
  // Authentication
  const { user, isAuthenticated } = useAuth();
  
  // State management
  const [mitzvot, setMitzvot] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [mitzvahOfTheDay, setMitzvahOfTheDay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedBook, setSelectedBook] = useState('all');
  const [viewMode, setViewMode] = useState('cards');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({});
  const [activeTab, setActiveTab] = useState('explore');
  const [quizData, setQuizData] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState('');
  const [showResult, setShowResult] = useState(false);
  const [score, setScore] = useState(0);
  const [userProgress, setUserProgress] = useState(null);
  const [flashcards, setFlashcards] = useState([]);
  const [currentFlashcardIndex, setCurrentFlashcardIndex] = useState(0);
  const [showFlashcardAnswer, setShowFlashcardAnswer] = useState(false);
  
  // Authentication UI state
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  const { toast } = useToast();

  // Status types for display
  const statusTypes = [
    { value: 'direct', label: 'Direct in Bible', color: 'bg-green-100 text-green-800' },
    { value: 'indirect', label: 'Indirect in Bible', color: 'bg-blue-100 text-blue-800' },
    { value: 'rabbinic', label: 'Rabbinic Origin', color: 'bg-purple-100 text-purple-800' },
    { value: 'traditional', label: 'Traditional', color: 'bg-orange-100 text-orange-800' }
  ];

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load mitzvot when filters change
  useEffect(() => {
    if (categories.length > 0) {
      loadMitzvot();
    }
  }, [searchTerm, selectedCategory, selectedStatus, selectedBook, currentPage, categories.length]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load stats, categories, mitzvah of the day, and user progress in parallel
      const promises = [
        apiService.getStats(),
        apiService.getCategories(),
        apiService.getMitzvahOfTheDay()
      ];
      
      // Only load progress if authenticated
      if (isAuthenticated) {
        promises.push(apiService.getUserProgress(user.id));
      }
      
      const responses = await Promise.all(promises);
      
      setStats(responses[0]);
      setCategories(responses[1]);
      setMitzvahOfTheDay(responses[2]);
      
      if (isAuthenticated && responses[3]) {
        setUserProgress(responses[3]);
      }
      
      // Load initial mitzvot data
      await loadMitzvot();
      
    } catch (error) {
      console.error('Error loading initial data:', error);
      toast({
        title: "Error Loading Data",
        description: "Failed to load initial data. Please refresh the page.",
        variant: "destructive",
      });
    }
  };

  const loadMitzvot = async () => {
    try {
      setLoading(true);

      const params = {
        search: searchTerm,
        category: selectedCategory,
        status: selectedStatus,
        book: selectedBook,
        page: currentPage,
        limit: 20
      };

      const response = await apiService.getMitzvot(params);
      
      setMitzvot(response.mitzvot);
      setTotalPages(response.totalPages);
      setFilters(response.filters);
      
    } catch (error) {
      console.error('Error loading mitzvot:', error);
      toast({
        title: "Error Loading Mitzvot",
        description: "Failed to load mitzvot data. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Handle search with debouncing
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setCurrentPage(1); // Reset to first page on new search
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [searchTerm]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedCategory, selectedStatus, selectedBook]);

  const getStatusColor = (status) => {
    const statusType = statusTypes.find(s => s.value === status);
    return statusType ? statusType.color : 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const statusType = statusTypes.find(s => s.value === status);
    return statusType ? statusType.label : status;
  };

  const getCategoryName = (categorySlug) => {
    const category = categories.find(c => c.slug === categorySlug);
    return category ? category.name : categorySlug;
  };

  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const MitzvahCard = ({ mitzvah }) => (
    <Card key={mitzvah.id} className="hover:shadow-lg transition-shadow duration-200">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <CardTitle className="text-lg font-semibold text-gray-900 leading-tight">
            #{mitzvah.number}: {mitzvah.title}
          </CardTitle>
          <Badge className={`ml-2 ${getStatusColor(mitzvah.status)}`}>
            {getStatusLabel(mitzvah.status)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-1">Traditional Wording:</h4>
            <p className="text-gray-600 italic">{mitzvah.traditionalWording}</p>
          </div>
          
          <div>
            <h4 className="font-medium text-gray-700 mb-1 flex items-center">
              <BookOpen className="w-4 h-4 mr-1" />
              Source:
            </h4>
            <p className="text-sm text-gray-600 bg-gray-50 p-2 rounded">
              {mitzvah.sourceVerse}
            </p>
          </div>

          <div>
            <h4 className="font-medium text-gray-700 mb-1 flex items-center">
              <Info className="w-4 h-4 mr-1" />
              Scholarly Note:
            </h4>
            <p className="text-sm text-gray-600">{mitzvah.scholarlyNote}</p>
          </div>

          <div className="flex flex-wrap gap-2 pt-2">
            <Badge variant="outline" className="text-xs">
              {getCategoryName(mitzvah.category)}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}
            </Badge>
          </div>

          <div className="flex flex-wrap gap-1 pt-1">
            {mitzvah.keywords.slice(0, 4).map((keyword, idx) => (
              <Badge key={idx} variant="secondary" className="text-xs">
                <Tag className="w-3 h-3 mr-1" />
                {keyword}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );

  const MitzvahTableRow = ({ mitzvah }) => (
    <tr key={mitzvah.id} className="border-b hover:bg-gray-50">
      <td className="py-3 px-4 font-medium">#{mitzvah.number}</td>
      <td className="py-3 px-4">
        <div className="font-medium text-gray-900">{mitzvah.title}</div>
        <div className="text-sm text-gray-600 mt-1">{mitzvah.traditionalWording}</div>
      </td>
      <td className="py-3 px-4 text-sm">{mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}</td>
      <td className="py-3 px-4">
        <Badge className={getStatusColor(mitzvah.status)}>
          {getStatusLabel(mitzvah.status)}
        </Badge>
      </td>
      <td className="py-3 px-4 text-sm">{getCategoryName(mitzvah.category)}</td>
    </tr>
  );

  const Pagination = () => {
    if (totalPages <= 1) return null;

    const pages = [];
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return (
      <div className="flex justify-center items-center space-x-2 mt-8">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          Previous
        </Button>
        
        {startPage > 1 && (
          <>
            <Button variant="outline" size="sm" onClick={() => handlePageChange(1)}>1</Button>
            {startPage > 2 && <span className="px-2">...</span>}
          </>
        )}
        
        {pages.map(page => (
          <Button
            key={page}
            variant={currentPage === page ? "default" : "outline"}
            size="sm"
            onClick={() => handlePageChange(page)}
          >
            {page}
          </Button>
        ))}
        
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="px-2">...</span>}
            <Button variant="outline" size="sm" onClick={() => handlePageChange(totalPages)}>
              {totalPages}
            </Button>
          </>
        )}
        
        <Button
          variant="outline"
          size="sm"
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          Next
        </Button>
      </div>
    );
  };

  // Quiz Functions
  const startQuiz = async (category = 'all') => {
    try {
      setLoading(true);
      const quizResponse = await apiService.getQuizQuestions(category, 5);
      setQuizData(quizResponse);
      setCurrentQuestionIndex(0);
      setSelectedAnswer('');
      setShowResult(false);
      setScore(0);
      setActiveTab('quiz');
      
      toast({
        title: "Quiz Started!",
        description: `Starting quiz with ${quizResponse.questions.length} questions.`,
      });
    } catch (error) {
      console.error('Error starting quiz:', error);
      toast({
        title: "Error",
        description: "Failed to start quiz. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const submitAnswer = () => {
    if (!selectedAnswer || !quizData) return;
    
    const currentQuestion = quizData.questions[currentQuestionIndex];
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;
    
    if (isCorrect) {
      setScore(score + 1);
    }
    
    setShowResult(true);
    
    setTimeout(() => {
      if (currentQuestionIndex < quizData.questions.length - 1) {
        setCurrentQuestionIndex(currentQuestionIndex + 1);
        setSelectedAnswer('');
        setShowResult(false);
      } else {
        // Quiz completed
        const finalScore = isCorrect ? score + 1 : score;
        toast({
          title: "Quiz Completed!",
          description: `Your score: ${finalScore}/${quizData.questions.length}`,
        });
      }
    }, 2000);
  };

  const resetQuiz = () => {
    setQuizData(null);
    setCurrentQuestionIndex(0);
    setSelectedAnswer('');
    setShowResult(false);
    setScore(0);
    setActiveTab('explore');
  };

  // Flashcard Functions
  const startFlashcards = async () => {
    try {
      setLoading(true);
      const userId = isAuthenticated ? user.id : 'guest_user';
      const flashcardResponse = await apiService.getFlashcards(userId, 10);
      setFlashcards(flashcardResponse.flashcards);
      setCurrentFlashcardIndex(0);
      setShowFlashcardAnswer(false);
      setActiveTab('flashcards');
      
      toast({
        title: "Flashcards Ready!",
        description: `Starting flashcard review with ${flashcardResponse.flashcards.length} cards.`,
      });
    } catch (error) {
      console.error('Error starting flashcards:', error);
      toast({
        title: "Error",
        description: "Failed to load flashcards. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const reviewFlashcard = async (correct) => {
    if (!flashcards[currentFlashcardIndex]) return;
    
    const flashcard = flashcards[currentFlashcardIndex].flashcard;
    const difficulty = correct ? Math.min(5, flashcard.difficulty + 1) : Math.max(1, flashcard.difficulty - 1);
    
    try {
      await apiService.reviewFlashcard(flashcard.id, difficulty, correct);
      
      // Update progress for the mitzvah (only if authenticated)
      if (isAuthenticated) {
        const mitzvah = flashcards[currentFlashcardIndex].mitzvah;
        await apiService.updateMitzvahProgress(mitzvah.id, correct, user.id);
      }
      
      toast({
        title: correct ? "Correct! ✅" : "Keep practicing! 📚",
        description: correct ? "Great job! Moving to next card." : "Don't worry, you'll get it next time!",
      });
      
      // Move to next flashcard
      setTimeout(() => {
        if (currentFlashcardIndex < flashcards.length - 1) {
          setCurrentFlashcardIndex(currentFlashcardIndex + 1);
          setShowFlashcardAnswer(false);
        } else {
          // Finished all flashcards
          toast({
            title: "Session Complete! 🎉",
            description: isAuthenticated 
              ? "Great work! Your progress has been saved. Come back tomorrow for more review."
              : "Great work! Sign up to save your progress and continue tomorrow.",
          });
          setActiveTab('progress');
          // Reload progress data if authenticated
          if (isAuthenticated) {
            loadUserProgress();
          }
        }
      }, 1500);
      
    } catch (error) {
      console.error('Error reviewing flashcard:', error);
      toast({
        title: "Error",
        description: "Failed to save review. Please try again.",
        variant: "destructive",
      });
    }
  };

  const loadUserProgress = async () => {
    if (!isAuthenticated) return;
    
    try {
      const progressResponse = await apiService.getUserProgress(user.id);
      setUserProgress(progressResponse);
    } catch (error) {
      console.error('Error loading progress:', error);
    }
  };

  if (loading && mitzvot.length === 0) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading the 613 Laws of the Bible...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-start mb-8">
          <div className="text-center flex-1">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              The 613 Laws of the Bible
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              Explore the complete collection of biblical commandments with their sources, 
              scholarly notes, and categorization. Search by content, filter by origin, 
              and discover the rich tradition of biblical law.
            </p>
          </div>
          
          {/* Authentication Section */}
          <div className="flex gap-2 ml-4">
            {isAuthenticated ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => setShowProfileModal(true)}
                  className="flex items-center gap-2"
                >
                  <User className="w-4 h-4" />
                  {user?.name || 'Profile'}
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => {
                    setAuthMode('login');
                    setShowAuthModal(true);
                  }}
                  className="flex items-center gap-2"
                >
                  <LogIn className="w-4 h-4" />
                  Sign In
                </Button>
                <Button
                  onClick={() => {
                    setAuthMode('register');
                    setShowAuthModal(true);
                  }}
                  className="flex items-center gap-2"
                >
                  <UserPlus className="w-4 h-4" />
                  Sign Up
                </Button>
              </>
            )}
          </div>
        </div>
        
        {/* Guest Mode Notice */}
        {!isAuthenticated && (
          <div className="mb-6">
            <Card className="bg-yellow-50 border-yellow-200">
              <CardContent className="pt-4">
                <div className="flex items-center gap-2 text-yellow-800">
                  <Info className="w-4 h-4" />
                  <span className="text-sm">
                    <strong>Guest Mode:</strong> You can explore and use all features, but your progress won't be saved. 
                    <button 
                      onClick={() => setShowAuthModal(true)}
                      className="text-yellow-900 underline hover:text-yellow-700 ml-1"
                    >
                      Sign up to save your progress!
                    </button>
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Mitzvah of the Day */}
        {mitzvahOfTheDay && (
          <div className="mb-8">
            <Card className="bg-gradient-to-r from-purple-500 to-indigo-600 text-white">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5" />
                  Mitzvah of the Day
                  <Badge variant="secondary" className="bg-white/20 text-white">
                    #{mitzvahOfTheDay.number}
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <h3 className="text-xl font-semibold">{mitzvahOfTheDay.title}</h3>
                  <p className="text-purple-100 italic">"{mitzvahOfTheDay.traditionalWording}"</p>
                  <p className="text-sm text-purple-200">
                    <strong>{mitzvahOfTheDay.sourceVerse}</strong>
                  </p>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      {getStatusLabel(mitzvahOfTheDay.status)}
                    </Badge>
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      {getCategoryName(mitzvahOfTheDay.category)}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Navigation Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="explore">Explore</TabsTrigger>
            <TabsTrigger value="quiz">Quiz</TabsTrigger>
            <TabsTrigger value="flashcards">Flashcards</TabsTrigger>
            <TabsTrigger value="progress">Progress</TabsTrigger>
          </TabsList>

          {/* Explore Tab Content */}
          <TabsContent value="explore">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <Card className="text-center">
                <CardContent className="pt-4">
                  <div className="text-2xl font-bold text-blue-600">{stats.totalMitzvot || 0}</div>
                  <div className="text-sm text-gray-600">Total Mitzvot</div>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent className="pt-4">
                  <div className="text-2xl font-bold text-green-600">{stats.directBiblical || 0}</div>
                  <div className="text-sm text-gray-600">Direct Biblical</div>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent className="pt-4">
                  <div className="text-2xl font-bold text-purple-600">{stats.categoriesCount || 0}</div>
                  <div className="text-sm text-gray-600">Categories</div>
                </CardContent>
              </Card>
              <Card className="text-center">
                <CardContent className="pt-4">
                  <div className="text-2xl font-bold text-orange-600">{mitzvot.length}</div>
                  <div className="text-sm text-gray-600">Current Results</div>
                </CardContent>
              </Card>
            </div>

            {/* Search and Filters */}
            <Card className="mb-8">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="lg:col-span-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder="Search mitzvot, keywords, or verses..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Categories" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      {categories.map((category) => (
                        <SelectItem key={category.id} value={category.slug}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Origins" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Origins</SelectItem>
                      {statusTypes.map((status) => (
                        <SelectItem key={status.value} value={status.value}>
                          {status.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={selectedBook} onValueChange={setSelectedBook}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Books" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Books</SelectItem>
                      {filters.books && filters.books.map((book) => (
                        <SelectItem key={book} value={book}>
                          {book}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* View Mode Tabs */}
            <Tabs value={viewMode} onValueChange={setViewMode} className="w-full">
              <TabsList>
                <TabsTrigger value="cards">Card View</TabsTrigger>
                <TabsTrigger value="table">Table View</TabsTrigger>
              </TabsList>

              <TabsContent value="cards" className="mt-6">
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {mitzvot.map((mitzvah) => (
                    <Card key={mitzvah.id} className="hover:shadow-lg transition-shadow">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <CardTitle className="text-lg leading-tight">
                            <span className="text-blue-600 font-bold">#{mitzvah.number}</span> {mitzvah.title}
                          </CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Traditional Wording:</p>
                            <p className="text-sm text-gray-600 italic">"{mitzvah.traditionalWording}"</p>
                          </div>
                          
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Source:</p>
                            <p className="text-sm text-gray-600">{mitzvah.sourceVerse}</p>
                          </div>
                          
                          <div>
                            <p className="text-sm font-medium text-gray-700 mb-1">Scholarly Note:</p>
                            <p className="text-sm text-gray-600">{mitzvah.scholarlyNote}</p>
                          </div>
                          
                          <div className="flex flex-wrap gap-2 pt-2">
                            <Badge className={getStatusColor(mitzvah.status)}>
                              {getStatusLabel(mitzvah.status)}
                            </Badge>
                            <Badge variant="outline">
                              {getCategoryName(mitzvah.category)}
                            </Badge>
                            <Badge variant="secondary">
                              {mitzvah.book}
                            </Badge>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="table" className="mt-6">
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="border-b bg-gray-50">
                          <tr>
                            <th className="text-left p-4 font-medium">#</th>
                            <th className="text-left p-4 font-medium">Title</th>
                            <th className="text-left p-4 font-medium">Traditional Wording</th>
                            <th className="text-left p-4 font-medium">Source</th>
                            <th className="text-left p-4 font-medium">Status</th>
                            <th className="text-left p-4 font-medium">Category</th>
                          </tr>
                        </thead>
                        <tbody>
                          {mitzvot.map((mitzvah) => (
                            <tr key={mitzvah.id} className="border-b hover:bg-gray-50">
                              <td className="p-4 text-blue-600 font-bold">#{mitzvah.number}</td>
                              <td className="p-4 font-medium">{mitzvah.title}</td>
                              <td className="p-4 text-gray-600 italic">"{mitzvah.traditionalWording}"</td>
                              <td className="p-4 text-sm text-gray-600">{mitzvah.sourceVerse}</td>
                              <td className="p-4">
                                <Badge className={getStatusColor(mitzvah.status)}>
                                  {getStatusLabel(mitzvah.status)}
                                </Badge>
                              </td>
                              <td className="p-4">
                                <Badge variant="outline">{getCategoryName(mitzvah.category)}</Badge>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {/* Pagination */}
            <Pagination />
          </TabsContent>

          {/* Quiz Tab Content */}
          <TabsContent value="quiz">
            {!quizData ? (
              <div className="text-center py-12">
                <Card className="max-w-2xl mx-auto">
                  <CardHeader>
                    <CardTitle className="text-2xl">🧠 Test Your Knowledge</CardTitle>
                    <p className="text-gray-600">
                      Challenge yourself with questions about the 613 mitzvot. Choose a category or test your overall knowledge!
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <Button onClick={() => startQuiz('all')} className="h-16">
                        <div className="text-center">
                          <div className="font-semibold">All Categories</div>
                          <div className="text-sm opacity-75">Mixed questions from all 613 mitzvot</div>
                        </div>
                      </Button>
                      {categories.slice(0, 6).map((category) => (
                        <Button
                          key={category.id}
                          variant="outline"
                          onClick={() => startQuiz(category.slug)}
                          className="h-16"
                        >
                          <div className="text-center">
                            <div className="font-semibold">{category.name}</div>
                            <div className="text-sm opacity-75">Focus on this category</div>
                          </div>
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto">
                {currentQuestionIndex < quizData.questions.length ? (
                  <Card>
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>
                          Question {currentQuestionIndex + 1} of {quizData.questions.length}
                        </CardTitle>
                        <Badge variant="outline">
                          Score: {score}/{currentQuestionIndex}
                        </Badge>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${((currentQuestionIndex + 1) / quizData.questions.length) * 100}%` }}
                        />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <h3 className="text-xl font-semibold">
                          {quizData.questions[currentQuestionIndex].question}
                        </h3>
                        
                        <div className="grid gap-3">
                          {quizData.questions[currentQuestionIndex].options.map((option, index) => (
                            <Button
                              key={index}
                              variant={selectedAnswer === option ? "default" : "outline"}
                              className="text-left h-auto p-4 justify-start"
                              onClick={() => setSelectedAnswer(option)}
                              disabled={showResult}
                            >
                              <div className="w-6 h-6 rounded-full border-2 border-current mr-3 flex items-center justify-center">
                                {String.fromCharCode(65 + index)}
                              </div>
                              {option}
                            </Button>
                          ))}
                        </div>

                        {showResult && (
                          <div className={`p-4 rounded-lg ${
                            selectedAnswer === quizData.questions[currentQuestionIndex].correct_answer
                              ? 'bg-green-100 border border-green-300'
                              : 'bg-red-100 border border-red-300'
                          }`}>
                            <p className={`font-semibold ${
                              selectedAnswer === quizData.questions[currentQuestionIndex].correct_answer
                                ? 'text-green-800'
                                : 'text-red-800'
                            }`}>
                              {selectedAnswer === quizData.questions[currentQuestionIndex].correct_answer
                                ? '✅ Correct!'
                                : '❌ Incorrect'
                              }
                            </p>
                            <p className="text-sm mt-2 text-gray-700">
                              {quizData.questions[currentQuestionIndex].explanation}
                            </p>
                          </div>
                        )}

                        <div className="flex justify-between">
                          <Button variant="outline" onClick={resetQuiz}>
                            Exit Quiz
                          </Button>
                          <Button 
                            onClick={submitAnswer} 
                            disabled={!selectedAnswer || showResult}
                          >
                            {currentQuestionIndex === quizData.questions.length - 1 ? 'Finish Quiz' : 'Next Question'}
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="text-center">
                    <CardHeader>
                      <CardTitle className="text-2xl">🎉 Quiz Complete!</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <div className="text-4xl font-bold text-blue-600">
                          {score}/{quizData.questions.length}
                        </div>
                        <p className="text-lg">
                          {score === quizData.questions.length ? 'Perfect Score! 🏆' :
                           score >= quizData.questions.length * 0.8 ? 'Excellent Work! 👏' :
                           score >= quizData.questions.length * 0.6 ? 'Good Job! 👍' :
                           'Keep Studying! 📚'}
                        </p>
                        <div className="flex gap-4 justify-center">
                          <Button onClick={() => startQuiz(quizData.category)}>
                            Try Again
                          </Button>
                          <Button variant="outline" onClick={resetQuiz}>
                            Back to Explore
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* Flashcards Tab Content */}
          <TabsContent value="flashcards">
            {flashcards.length === 0 ? (
              <div className="text-center py-12">
                <Card className="max-w-2xl mx-auto">
                  <CardHeader>
                    <CardTitle className="text-2xl">📚 Flashcard Review</CardTitle>
                    <p className="text-gray-600">
                      Use spaced repetition to master the mitzvot! The algorithm will show you cards when you need to review them.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <Button onClick={startFlashcards} className="h-16 w-full">
                      <div className="text-center">
                        <div className="font-semibold">Start Flashcard Review</div>
                        <div className="text-sm opacity-75">Review cards due today</div>
                      </div>
                    </Button>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <div className="max-w-2xl mx-auto">
                {currentFlashcardIndex < flashcards.length ? (
                  <Card>
                    <CardHeader>
                      <div className="flex justify-between items-center">
                        <CardTitle>
                          Card {currentFlashcardIndex + 1} of {flashcards.length}
                        </CardTitle>
                        <Badge variant="outline">
                          #{flashcards[currentFlashcardIndex].mitzvah.number}
                        </Badge>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${((currentFlashcardIndex + 1) / flashcards.length) * 100}%` }}
                        />
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-6">
                        <div className="text-center">
                          <h3 className="text-xl font-semibold mb-4">
                            {flashcards[currentFlashcardIndex].mitzvah.title}
                          </h3>
                          
                          {!showFlashcardAnswer ? (
                            <div className="space-y-4">
                              <p className="text-gray-600">
                                What is the traditional wording for this mitzvah?
                              </p>
                              <Button 
                                onClick={() => setShowFlashcardAnswer(true)}
                                variant="outline"
                                className="w-full h-12"
                              >
                                Show Answer
                              </Button>
                            </div>
                          ) : (
                            <div className="space-y-4">
                              <div className="bg-blue-50 p-4 rounded-lg">
                                <p className="font-medium text-blue-900 italic">
                                  "{flashcards[currentFlashcardIndex].mitzvah.traditionalWording}"
                                </p>
                              </div>
                              <div className="bg-gray-50 p-4 rounded-lg">
                                <p className="text-sm text-gray-700">
                                  <strong>Source:</strong> {flashcards[currentFlashcardIndex].mitzvah.sourceVerse}
                                </p>
                              </div>
                              
                              <div className="flex gap-4 justify-center pt-4">
                                <Button 
                                  onClick={() => reviewFlashcard(false)}
                                  variant="outline"
                                  className="flex items-center gap-2 h-12 px-6"
                                >
                                  <span className="text-red-500">❌</span>
                                  Incorrect
                                </Button>
                                <Button 
                                  onClick={() => reviewFlashcard(true)}
                                  className="flex items-center gap-2 h-12 px-6"
                                >
                                  <span className="text-green-500">✅</span>
                                  Correct
                                </Button>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card className="text-center">
                    <CardHeader>
                      <CardTitle className="text-2xl">🎉 Review Complete!</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        <p className="text-lg">Great work! You've reviewed all your flashcards for today.</p>
                        <div className="flex gap-4 justify-center">
                          <Button onClick={startFlashcards}>
                            Review More Cards
                          </Button>
                          <Button variant="outline" onClick={() => setActiveTab('progress')}>
                            View Progress
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </TabsContent>

          {/* Progress Tab Content */}
          <TabsContent value="progress">
            <div className="space-y-8">
              {userProgress && (
                <>
                  {/* Overall Progress */}
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <span className="text-2xl">📊</span>
                        Your Learning Progress
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-blue-50 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">{userProgress.learning}</div>
                          <div className="text-sm text-gray-600">Learning</div>
                        </div>
                        <div className="text-center p-4 bg-yellow-50 rounded-lg">
                          <div className="text-2xl font-bold text-yellow-600">{userProgress.reviewing}</div>
                          <div className="text-sm text-gray-600">Reviewing</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">{userProgress.mastered}</div>
                          <div className="text-sm text-gray-600">Mastered</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg">
                          <div className="text-2xl font-bold text-purple-600">{userProgress.overallProgress}%</div>
                          <div className="text-sm text-gray-600">Overall</div>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <div className="flex justify-between text-sm text-gray-600 mb-2">
                          <span>Progress</span>
                          <span>{userProgress.mastered} / {userProgress.totalMitzvot}</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-3">
                          <div 
                            className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-500"
                            style={{ width: `${userProgress.overallProgress}%` }}
                          />
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Category Progress */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Progress by Category</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4">
                        {Object.entries(userProgress.categoryProgress).map(([categoryName, progress]) => (
                          <div key={categoryName} className="space-y-2">
                            <div className="flex justify-between text-sm">
                              <span className="font-medium">{categoryName}</span>
                              <span className="text-gray-600">{progress.mastered} / {progress.total} ({progress.percentage}%)</span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${progress.percentage}%` }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Quick Actions */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <Button onClick={startFlashcards} variant="outline" className="h-16">
                          <div className="text-center">
                            <div className="font-semibold">📚 Study Flashcards</div>
                            <div className="text-sm opacity-75">Review due cards</div>
                          </div>
                        </Button>
                        <Button onClick={() => startQuiz('all')} variant="outline" className="h-16">
                          <div className="text-center">
                            <div className="font-semibold">🧠 Take Quiz</div>
                            <div className="text-sm opacity-75">Test your knowledge</div>
                          </div>
                        </Button>
                        <Button onClick={() => setActiveTab('explore')} variant="outline" className="h-16">
                          <div className="text-center">
                            <div className="font-semibold">🔍 Explore</div>
                            <div className="text-sm opacity-75">Browse mitzvot</div>
                          </div>
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>
          </TabsContent>

        </Tabs>
      </div>
      
      {/* Authentication Modals */}
      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode={authMode}
      />
      
      {/* User Profile Modal */}
      {showProfileModal && (
        <UserProfile onClose={() => setShowProfileModal(false)} />
      )}
      
      <Toaster />
    </div>
  );
};

export default MitzvotApp;