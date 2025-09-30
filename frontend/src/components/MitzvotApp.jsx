import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, BookOpen, Tag, Info, Loader, User, UserPlus, LogIn, ChevronDown, ChevronLeft, ChevronRight, Expand, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from './ui/dropdown-menu';
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
  const [contentType, setContentType] = useState('mitzvot'); // 'mitzvot' or 'precepts'
  const [mitzvot, setMitzvot] = useState([]);
  const [precepts, setPrecepts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [preceptsStats, setPreceptsStats] = useState({});
  const [mitzvahOfTheDay, setMitzvahOfTheDay] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
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
  
  // Precepts interaction state
  const [expandedVerses, setExpandedVerses] = useState({}); // Track which verses are expanded
  const [preceptVerseIndex, setPreceptVerseIndex] = useState({}); // Track current verse index for each precept

  const { toast } = useToast();

  // Status types removed - no longer using origin-based filtering
  // All mitzvot are considered biblical commands

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  // Load content when filters change or content type changes
  useEffect(() => {
    if (categories.length > 0) {
      loadContent();
    }
  }, [contentType, searchTerm, selectedCategory, selectedBook, currentPage, categories.length]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load stats, categories, mitzvah of the day, precepts stats, and user progress in parallel
      const promises = [
        apiService.getStats(),
        apiService.getCategories(),
        apiService.getMitzvahOfTheDay(),
        apiService.getPreceptsStats()
      ];
      
      // Only load progress if authenticated
      if (isAuthenticated) {
        promises.push(apiService.getUserProgress(user.id));
      }
      
      const responses = await Promise.all(promises);
      
      setStats(responses[0]);
      setCategories(responses[1]);
      setMitzvahOfTheDay(responses[2]);
      setPreceptsStats(responses[3]);
      
      if (isAuthenticated && responses[responses.length - 1]) {
        setUserProgress(responses[responses.length - 1]);
      }
      
      // Load initial content based on content type
      await loadContent();
      
    } catch (error) {
      console.error('Error loading initial data:', error);
      toast({
        title: "Error Loading Data",
        description: "Failed to load initial data. Please refresh the page.",
        variant: "destructive",
      });
    }
  };

  const loadContent = async () => {
    if (contentType === 'mitzvot') {
      await loadMitzvot();
    } else {
      await loadPrecepts();
    }
  };

  const loadMitzvot = async () => {
    try {
      setLoading(true);

      const params = {
        search: searchTerm,
        category: selectedCategory,
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

  const loadPrecepts = async () => {
    try {
      setLoading(true);

      const params = {
        search: searchTerm,
        testament: selectedCategory, // Using selectedCategory for testament filter
        page: currentPage,
        limit: 20
      };

      const response = await apiService.getPrecepts(params);
      
      setPrecepts(response.precepts);
      setTotalPages(response.totalPages);
      setFilters(response.filters);
      
    } catch (error) {
      console.error('Error loading precepts:', error);
      toast({
        title: "Error Loading Precepts",
        description: "Failed to load precepts data. Please try again.",
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
  }, [selectedCategory, selectedBook]);

  const getCategoryName = (categorySlug) => {
    const category = categories.find(c => c.slug === categorySlug);
    return category ? category.name : categorySlug;
  };

  // Precepts verse interaction handlers
  const toggleVerseExpansion = (preceptId, verseIndex) => {
    const key = `${preceptId}_${verseIndex}`;
    setExpandedVerses(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const navigateVerse = (preceptId, direction) => {
    const precept = precepts.find(p => p.id === preceptId);
    if (!precept?.verses?.length) return;

    const currentIndex = preceptVerseIndex[preceptId] || 0;
    let newIndex;

    if (direction === 'prev') {
      newIndex = currentIndex > 0 ? currentIndex - 1 : precept.verses.length - 1;
    } else {
      newIndex = currentIndex < precept.verses.length - 1 ? currentIndex + 1 : 0;
    }

    setPreceptVerseIndex(prev => ({
      ...prev,
      [preceptId]: newIndex
    }));
  };

  const getVerseReference = (verse) => {
    return `${verse.book} ${verse.chapter}:${verse.verse}`;
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
          <Badge className="ml-2 bg-blue-100 text-blue-800">
            {mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <h4 className="font-medium text-gray-700 mb-1 flex items-center">
              <BookOpen className="w-4 h-4 mr-1" />
              Biblical Source ({mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}):
            </h4>
            <p className="text-gray-600 italic bg-gray-50 p-3 rounded border-l-4 border-blue-200">
              "{mitzvah.sourceVerse}"
            </p>
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
        <div className="text-sm text-gray-600 mt-1 italic">"{mitzvah.sourceVerse.substring(0, 60)}..."</div>
      </td>
      <td className="py-3 px-4 text-sm">{mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}</td>
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

  const startPreceptsQuiz = async (testament = 'all') => {
    try {
      setLoading(true);
      
      // Create a simple demo quiz for precepts
      const demoQuestions = [
        {
          question: "Which precept deals with forbidden foods in the Bible?",
          answers: ["Abomination", "Adultery", "Acceptable", "Affections"],
          correctAnswer: "Abomination"
        },
        {
          question: "Which testament classification is most common in our precepts collection?",
          answers: ["Old Testament", "New Testament", "Mixed Testament"],
          correctAnswer: "Mixed Testament"
        },
        {
          question: "What does the precept 'Acceptable' primarily concern?",
          answers: ["Offerings to God", "Marriage rules", "Dietary laws", "Sabbath observance"],
          correctAnswer: "Offerings to God"
        },
        {
          question: "How many total precepts are currently in the collection?",
          answers: ["15", "20", "23", "30"],
          correctAnswer: "23"
        },
        {
          question: "Which book contains many of the precepts about dietary laws?",
          answers: ["Genesis", "Deuteronomy", "Psalms", "Matthew"],
          correctAnswer: "Deuteronomy"
        }
      ];
      
      // Filter questions based on testament if needed
      let filteredQuestions = demoQuestions;
      if (testament === 'old') {
        filteredQuestions = demoQuestions.slice(0, 3); // First 3 questions focus on OT
      } else if (testament === 'new') {
        filteredQuestions = [demoQuestions[1], demoQuestions[3]]; // Fewer NT focused questions
      }
      
      setQuizData({ questions: filteredQuestions });
      setCurrentQuestionIndex(0);
      setSelectedAnswer('');
      setShowResult(false);
      setScore(0);
      setActiveTab('quiz');
      
      toast({
        title: "Precepts Quiz Started!",
        description: `Starting quiz with ${filteredQuestions.length} questions about biblical precepts.`,
      });
    } catch (error) {
      console.error('Error starting precepts quiz:', error);
      toast({
        title: "Error",
        description: "Failed to start precepts quiz. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const generatePreceptsQuizQuestions = (precepts, count) => {
    if (!precepts || precepts.length === 0) {
      return [];
    }

    const questions = [];
    const shuffledPrecepts = [...precepts].sort(() => Math.random() - 0.5);
    
    for (let i = 0; i < Math.min(count, shuffledPrecepts.length); i++) {
      const precept = shuffledPrecepts[i];
      
      // Generate different types of questions
      const questionTypes = [
        () => generateVerseToTitleQuestion(precept, precepts),
        () => generateTitleToTestamentQuestion(precept, precepts),
        () => generateTopicToTitleQuestion(precept, precepts)
      ];
      
      const randomType = questionTypes[Math.floor(Math.random() * questionTypes.length)];
      
      try {
        const question = randomType();
        if (question) {
          questions.push(question);
        }
      } catch (error) {
        console.error('Error generating question:', error);
        // Continue with next question
      }
    }
    
    return questions;
  };

  const generateVerseToTitleQuestion = (correctPrecept, allPrecepts) => {
    if (!correctPrecept || !correctPrecept.verses || correctPrecept.verses.length === 0) return null;
    
    const randomVerse = correctPrecept.verses[Math.floor(Math.random() * correctPrecept.verses.length)];
    if (!randomVerse || !randomVerse.text) return null;
    
    const wrongAnswers = allPrecepts
      .filter(p => p && p.id !== correctPrecept.id && p.title)
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);
    
    if (wrongAnswers.length < 3) return null;
    
    const answers = [correctPrecept, ...wrongAnswers]
      .sort(() => Math.random() - 0.5)
      .map(p => p.title);
    
    const verseText = randomVerse.text.substring(0, 100);
    const verseRef = `${randomVerse.book || ''} ${randomVerse.chapter || ''}:${randomVerse.verse || ''}`;
    
    return {
      question: `Which precept is associated with this verse: "${verseText}..." (${verseRef})`,
      answers,
      correctAnswer: correctPrecept.title
    };
  };

  const generateTitleToTestamentQuestion = (correctPrecept, allPrecepts) => {
    if (!correctPrecept || !correctPrecept.testament || !correctPrecept.title) return null;
    
    const answers = ['Old Testament', 'New Testament', 'Mixed Testament'];
    
    const correctAnswer = correctPrecept.testament.charAt(0).toUpperCase() + correctPrecept.testament.slice(1) + ' Testament';
    
    return {
      question: `Which testament classification best describes the precept "${correctPrecept.title}"?`,
      answers,
      correctAnswer
    };
  };

  const generateTopicToTitleQuestion = (correctPrecept, allPrecepts) => {
    if (!correctPrecept || !correctPrecept.topics || correctPrecept.topics.length === 0) return null;
    
    const randomTopic = correctPrecept.topics[Math.floor(Math.random() * correctPrecept.topics.length)];
    if (!randomTopic) return null;
    
    const wrongAnswers = allPrecepts
      .filter(p => p && p.id !== correctPrecept.id && p.title)
      .sort(() => Math.random() - 0.5)
      .slice(0, 3);
    
    if (wrongAnswers.length < 3) return null;
    
    const answers = [correctPrecept, ...wrongAnswers]
      .sort(() => Math.random() - 0.5)
      .map(p => p.title);
    
    return {
      question: `Which precept is most associated with the topic "${randomTopic.replace('-', ' ')}"?`,
      answers,
      correctAnswer: correctPrecept.title
    };
  };

  const submitAnswer = () => {
    if (!selectedAnswer || !quizData) return;
    
    const currentQuestion = quizData.questions[currentQuestionIndex];
    const isCorrect = selectedAnswer === currentQuestion.correct_answer;
    
    if (isCorrect) {
      setScore(score + 1);
    }
    
    setShowResult(true);
    
    // Auto-advance timing: 3-4 seconds for correct answers, 5-6 seconds for wrong answers
    const autoAdvanceDelay = isCorrect ? 3500 : 5500; // 3.5s correct, 5.5s incorrect
    
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
    }, autoAdvanceDelay);
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

  const startPreceptsFlashcards = async () => {
    try {
      setLoading(true);
      
      // Generate precepts flashcards from current data
      const preceptsFlashcards = generatePreceptsFlashcards(precepts, 10);
      
      if (preceptsFlashcards.length === 0) {
        toast({
          title: "No Precepts Available",
          description: "No precepts available for flashcard review.",
          variant: "destructive",
        });
        return;
      }

      setFlashcards(preceptsFlashcards);
      setCurrentFlashcardIndex(0);
      setShowFlashcardAnswer(false);
      setActiveTab('flashcards');
      
      toast({
        title: "Precepts Flashcards Ready!",
        description: `Starting precepts review with ${preceptsFlashcards.length} cards.`,
      });
    } catch (error) {
      console.error('Error starting precepts flashcards:', error);
      toast({
        title: "Error",
        description: "Failed to load precepts flashcards. Please try again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const generatePreceptsFlashcards = (precepts, count) => {
    const shuffledPrecepts = [...precepts].sort(() => Math.random() - 0.5);
    
    return shuffledPrecepts.slice(0, count).map((precept, index) => ({
      id: `precept_${precept.id}_${index}`,
      precept: precept,
      type: 'precept',
      difficulty: 1,
      nextReview: new Date()
    }));
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

  const reviewPreceptsFlashcard = async (correct) => {
    if (!flashcards[currentFlashcardIndex]) return;
    
    try {
      toast({
        title: correct ? "Excellent! ✅" : "Keep studying! 📚",
        description: correct ? "You're mastering biblical precepts!" : "Review the verses and try again later.",
      });
      
      // Move to next flashcard
      setTimeout(() => {
        if (currentFlashcardIndex < flashcards.length - 1) {
          setCurrentFlashcardIndex(currentFlashcardIndex + 1);
          setShowFlashcardAnswer(false);
        } else {
          // Finished all flashcards
          toast({
            title: "Precepts Study Complete! 🎉",
            description: "Great work studying biblical precepts! Continue exploring to deepen your understanding.",
          });
          setActiveTab('explore');
        }
      }, 1500);
      
    } catch (error) {
      console.error('Error reviewing precepts flashcard:', error);
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
          <p className="text-gray-600">Loading Biblical Study Suite...</p>
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
              {contentType === 'mitzvot' ? 'The 613 Laws of the Bible' : 'Biblical Precepts'}
            </h1>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              {contentType === 'mitzvot' 
                ? 'Explore the complete collection of biblical commandments with their sources and categorization. Search by content, filter by origin, and discover the rich tradition of biblical law.'
                : 'Discover comprehensive biblical precepts organized by topic with verse references and divine name accuracy. Search through teachings that span both Old and New Testament wisdom.'
              }
            </p>
          </div>
          
          {/* Authentication Section - Subtle User Menu */}
          <div className="ml-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button 
                  variant="ghost" 
                  size="sm"
                  className="flex items-center gap-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100"
                >
                  <User className="w-4 h-4" />
                  {isAuthenticated ? (
                    <>
                      <span className="hidden sm:inline">{user?.name || 'Account'}</span>
                      <ChevronDown className="w-3 h-3" />
                    </>
                  ) : (
                    <>
                      <span className="hidden sm:inline">Account</span>
                      <ChevronDown className="w-3 h-3" />
                    </>
                  )}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                {isAuthenticated ? (
                  <>
                    <DropdownMenuItem 
                      onClick={() => setShowProfileModal(true)}
                      className="flex items-center gap-2"
                    >
                      <User className="w-4 h-4" />
                      Profile
                    </DropdownMenuItem>
                  </>
                ) : (
                  <>
                    <DropdownMenuItem
                      onClick={() => {
                        setAuthMode('login');
                        setShowAuthModal(true);
                      }}
                      className="flex items-center gap-2"
                    >
                      <LogIn className="w-4 h-4" />
                      Sign In
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={() => {
                        setAuthMode('register');
                        setShowAuthModal(true);
                      }}
                      className="flex items-center gap-2"
                    >
                      <UserPlus className="w-4 h-4" />
                      Sign Up
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
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
                  <p className="text-purple-100 italic bg-white/10 p-3 rounded border-l-4 border-white/30">
                    "{mitzvahOfTheDay.sourceVerse}"
                  </p>
                  <div className="flex flex-wrap gap-2 pt-2">
                    <Badge variant="secondary" className="bg-white/20 text-white">
                      {mitzvahOfTheDay.book} {mitzvahOfTheDay.chapter}:{mitzvahOfTheDay.verse}
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

        {/* Content Type Switcher */}
        <div className="flex justify-center mb-6">
          <Tabs value={contentType} onValueChange={setContentType} className="w-auto">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="mitzvot">613 Mitzvot</TabsTrigger>
              <TabsTrigger value="precepts">Biblical Precepts</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

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
              {contentType === 'mitzvot' ? (
                <>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-blue-600">{stats.totalMitzvot || 0}</div>
                      <div className="text-sm text-gray-600">Total Mitzvot</div>
                    </CardContent>
                  </Card>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-green-600">{stats.booksCount || 0}</div>
                      <div className="text-sm text-gray-600">Books of Torah</div>
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
                </>
              ) : (
                <>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-blue-600">{preceptsStats.totalPrecepts || 0}</div>
                      <div className="text-sm text-gray-600">Total Precepts</div>
                    </CardContent>
                  </Card>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-green-600">{preceptsStats.totalVerses || 0}</div>
                      <div className="text-sm text-gray-600">Verse References</div>
                    </CardContent>
                  </Card>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-purple-600">{preceptsStats.uniqueTopics || 0}</div>
                      <div className="text-sm text-gray-600">Unique Topics</div>
                    </CardContent>
                  </Card>
                  <Card className="text-center">
                    <CardContent className="pt-4">
                      <div className="text-2xl font-bold text-orange-600">{precepts.length}</div>
                      <div className="text-sm text-gray-600">Current Results</div>
                    </CardContent>
                  </Card>
                </>
              )}
            </div>

            {/* Search and Filters */}
            <Card className="mb-8">
              <CardContent className="pt-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div className="lg:col-span-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                      <Input
                        placeholder={contentType === 'mitzvot' ? "Search mitzvot, keywords, or verses..." : "Search precepts, topics, or verses..."}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  
                  {contentType === 'mitzvot' ? (
                    <>
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
                    </>
                  ) : (
                    <>
                      <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                        <SelectTrigger>
                          <SelectValue placeholder="All Testaments" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="all">All Testaments</SelectItem>
                          <SelectItem value="old">Old Testament</SelectItem>
                          <SelectItem value="new">New Testament</SelectItem>
                        </SelectContent>
                      </Select>
                      <div></div> {/* Empty div to maintain grid layout */}
                    </>
                  )}
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
                  {contentType === 'mitzvot' ? (
                    mitzvot.map((mitzvah) => (
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
                              <p className="text-sm font-medium text-gray-700 mb-1">Biblical Source ({mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}):</p>
                              <p className="text-sm text-gray-600 italic bg-gray-50 p-2 rounded border-l-4 border-blue-200">"{mitzvah.sourceVerse}"</p>
                            </div>
                            
                            <div className="flex flex-wrap gap-2 pt-2">
                              <Badge variant="secondary">
                                {mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}
                              </Badge>
                              <Badge variant="outline">
                                {getCategoryName(mitzvah.category)}
                              </Badge>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))
                  ) : (
                    (precepts || []).map((precept) => {
                      const currentVerseIndex = preceptVerseIndex[precept.id] || 0;
                      const currentVerse = precept.verses?.[currentVerseIndex];
                      const expandKey = `${precept.id}_${currentVerseIndex}`;
                      const isExpanded = expandedVerses[expandKey];

                      return (
                        <Card key={precept.id} className="hover:shadow-lg transition-shadow">
                          <CardHeader>
                            <div className="flex items-start justify-between">
                              <CardTitle className="text-lg leading-tight">
                                <span className="text-purple-600 font-bold">📜</span> {precept.title}
                              </CardTitle>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-4">
                              {/* Verse Navigation */}
                              {precept.verses?.length > 0 && (
                                <div>
                                  <div className="flex items-center justify-between mb-2">
                                    <p className="text-sm font-medium text-gray-700">
                                      Verses ({precept.verses?.length || 0} references):
                                    </p>
                                    {precept.verses && precept.verses.length > 1 && (
                                      <div className="flex items-center gap-2">
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          onClick={() => navigateVerse(precept.id, 'prev')}
                                          className="h-6 w-6 p-0"
                                        >
                                          <ChevronLeft className="h-3 w-3" />
                                        </Button>
                                        <span className="text-xs text-gray-500">
                                          {currentVerseIndex + 1} of {precept.verses?.length || 0}
                                        </span>
                                        <Button
                                          variant="ghost"
                                          size="sm"
                                          onClick={() => navigateVerse(precept.id, 'next')}
                                          className="h-6 w-6 p-0"
                                        >
                                          <ChevronRight className="h-3 w-3" />
                                        </Button>
                                      </div>
                                    )}
                                  </div>

                                  {/* Current Verse Display */}
                                  {currentVerse && (
                                    <div className="mb-2">
                                      <div className="flex items-center justify-between mb-1">
                                        <p className="text-xs text-gray-500 font-medium">
                                          {getVerseReference(currentVerse)}
                                        </p>
                                        <div className="flex items-center gap-1">
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => toggleVerseExpansion(precept.id, currentVerseIndex)}
                                            className="h-6 px-2 text-xs"
                                          >
                                            <Expand className="h-3 w-3 mr-1" />
                                            {isExpanded ? 'Collapse' : 'Expand'}
                                          </Button>
                                          <Button
                                            variant="ghost"
                                            size="sm"
                                            className="h-6 px-2 text-xs text-blue-600"
                                            title="View in Bible (Coming Soon)"
                                          >
                                            <ExternalLink className="h-3 w-3 mr-1" />
                                            Bible
                                          </Button>
                                        </div>
                                      </div>
                                      
                                      <div className="text-sm text-gray-600 italic bg-gray-50 p-3 rounded border-l-4 border-purple-200">
                                        <p>
                                          "{isExpanded ? currentVerse.text : (currentVerse.text?.substring(0, 120) + (currentVerse.text?.length > 120 ? '...' : ''))}"
                                        </p>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                              
                              {/* Topics and Testament Badges */}
                              <div className="flex flex-wrap gap-2 pt-2 border-t border-gray-100">
                                <Badge variant="secondary" className="capitalize">
                                  {precept.testament} Testament
                                </Badge>
                                {precept.topics?.slice(0, 2).map((topic) => (
                                  <Badge key={topic} variant="outline" className="capitalize">
                                    {topic.replace('-', ' ')}
                                  </Badge>
                                ))}
                                {precept.topics?.length > 2 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{precept.topics.length - 2} more
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      );
                    })
                  )}
                </div>
              </TabsContent>

              <TabsContent value="table" className="mt-6">
                <Card>
                  <CardContent className="p-0">
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead className="border-b bg-gray-50">
                          <tr>
                            {contentType === 'mitzvot' ? (
                              <>
                                <th className="text-left p-4 font-medium">#</th>
                                <th className="text-left p-4 font-medium">Title</th>
                                <th className="text-left p-4 font-medium">Biblical Verse</th>
                                <th className="text-left p-4 font-medium">Source</th>
                                <th className="text-left p-4 font-medium">Category</th>
                              </>
                            ) : (
                              <>
                                <th className="text-left p-4 font-medium">Topic</th>
                                <th className="text-left p-4 font-medium">Verses</th>
                                <th className="text-left p-4 font-medium">Testament</th>
                                <th className="text-left p-4 font-medium">Topics</th>
                              </>
                            )}
                          </tr>
                        </thead>
                        <tbody>
                          {contentType === 'mitzvot' ? (
                            mitzvot.map((mitzvah) => (
                              <tr key={mitzvah.id} className="border-b hover:bg-gray-50">
                                <td className="p-4 text-blue-600 font-bold">#{mitzvah.number}</td>
                                <td className="p-4 font-medium">{mitzvah.title}</td>
                                <td className="p-4 text-gray-600 italic">"{mitzvah.sourceVerse.substring(0, 80)}..."</td>
                                <td className="p-4 text-sm text-gray-600">{mitzvah.book} {mitzvah.chapter}:{mitzvah.verse}</td>
                                <td className="p-4">
                                  <Badge variant="outline">{getCategoryName(mitzvah.category)}</Badge>
                                </td>
                              </tr>
                            ))
                          ) : (
                            precepts.map((precept) => (
                              <tr key={precept.id} className="border-b hover:bg-gray-50">
                                <td className="p-4 font-medium">{precept.title}</td>
                                <td className="p-4 text-sm text-gray-600">
                                  {precept.verses?.length || 0} references
                                  {precept.verses?.[0] && (
                                    <div className="text-xs text-gray-500 mt-1">
                                      {precept.verses[0].book} {precept.verses[0].chapter}:{precept.verses[0].verse}
                                    </div>
                                  )}
                                </td>
                                <td className="p-4">
                                  <Badge variant="secondary" className="capitalize">
                                    {precept.testament}
                                  </Badge>
                                </td>
                                <td className="p-4">
                                  <div className="flex flex-wrap gap-1">
                                    {precept.topics?.slice(0, 2).map((topic) => (
                                      <Badge key={topic} variant="outline" className="text-xs capitalize">
                                        {topic.replace('-', ' ')}
                                      </Badge>
                                    ))}
                                  </div>
                                </td>
                              </tr>
                            ))
                          )}
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
                      {contentType === 'mitzvot' 
                        ? 'Challenge yourself with questions about the 613 mitzvot. Choose a category or test your overall knowledge!'
                        : 'Test your understanding of biblical precepts. Choose a testament focus or test your comprehensive knowledge!'
                      }
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {contentType === 'mitzvot' ? (
                        <>
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
                        </>
                      ) : (
                        <>
                          <Button onClick={() => startPreceptsQuiz('all')} className="h-16">
                            <div className="text-center">
                              <div className="font-semibold">All Precepts</div>
                              <div className="text-sm opacity-75">Mixed questions from all biblical precepts</div>
                            </div>
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => startPreceptsQuiz('old')}
                            className="h-16"
                          >
                            <div className="text-center">
                              <div className="font-semibold">Old Testament</div>
                              <div className="text-sm opacity-75">Focus on Old Testament precepts</div>
                            </div>
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => startPreceptsQuiz('new')}
                            className="h-16"
                          >
                            <div className="text-center">
                              <div className="font-semibold">New Testament</div>
                              <div className="text-sm opacity-75">Focus on New Testament precepts</div>
                            </div>
                          </Button>
                          <Button
                            variant="outline"
                            onClick={() => startPreceptsQuiz('mixed')}
                            className="h-16"
                          >
                            <div className="text-center">
                              <div className="font-semibold">Mixed Testament</div>
                              <div className="text-sm opacity-75">Precepts spanning both testaments</div>
                            </div>
                          </Button>
                        </>
                      )}
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
                      {contentType === 'mitzvot' 
                        ? 'Use spaced repetition to master the mitzvot! The algorithm will show you cards when you need to review them.'
                        : 'Use spaced repetition to master biblical precepts! Study key verses and topics with our adaptive learning system.'
                      }
                    </p>
                  </CardHeader>
                  <CardContent>
                    {contentType === 'mitzvot' ? (
                      <Button onClick={startFlashcards} className="h-16 w-full">
                        <div className="text-center">
                          <div className="font-semibold">Start Flashcard Review</div>
                          <div className="text-sm opacity-75">Review mitzvot cards due today</div>
                        </div>
                      </Button>
                    ) : (
                      <Button onClick={startPreceptsFlashcards} className="h-16 w-full">
                        <div className="text-center">
                          <div className="font-semibold">Start Precepts Review</div>
                          <div className="text-sm opacity-75">Study biblical precepts and verses</div>
                        </div>
                      </Button>
                    )}
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
                          {flashcards[currentFlashcardIndex].type === 'precept' ? '📜' : `#${flashcards[currentFlashcardIndex].mitzvah?.number}`}
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
                          {flashcards[currentFlashcardIndex].type === 'precept' ? (
                            // Precepts flashcard
                            <>
                              <h3 className="text-xl font-semibold mb-4">
                                📜 {flashcards[currentFlashcardIndex].precept.title}
                              </h3>
                              
                              {!showFlashcardAnswer ? (
                                <div className="space-y-4">
                                  <p className="text-gray-600">
                                    What testament classification and key verses are associated with this precept?
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
                                  <div className="bg-purple-50 p-4 rounded-lg">
                                    <div className="space-y-2">
                                      <Badge className="capitalize">
                                        {flashcards[currentFlashcardIndex].precept.testament} Testament
                                      </Badge>
                                      <p className="text-sm text-purple-700">
                                        {flashcards[currentFlashcardIndex].precept.verses?.length || 0} verse references
                                      </p>
                                    </div>
                                  </div>
                                  
                                  {flashcards[currentFlashcardIndex].precept.verses?.[0] && (
                                    <div className="bg-gray-50 p-4 rounded-lg">
                                      <p className="text-sm text-gray-700 italic">
                                        "{flashcards[currentFlashcardIndex].precept.verses[0].text?.substring(0, 120)}..."
                                      </p>
                                      <p className="text-xs text-gray-500 mt-2">
                                        {getVerseReference(flashcards[currentFlashcardIndex].precept.verses[0])}
                                      </p>
                                    </div>
                                  )}
                                  
                                  <div className="flex gap-4 justify-center pt-4">
                                    <Button 
                                      onClick={() => reviewPreceptsFlashcard(false)}
                                      variant="outline"
                                      className="flex items-center gap-2 h-12 px-6"
                                    >
                                      <span className="text-red-500">❌</span>
                                      Difficult
                                    </Button>
                                    <Button 
                                      onClick={() => reviewPreceptsFlashcard(true)}
                                      className="flex items-center gap-2 h-12 px-6"
                                    >
                                      <span className="text-green-500">✅</span>
                                      Got It
                                    </Button>
                                  </div>
                                </div>
                              )}
                            </>
                          ) : (
                            // Mitzvot flashcard (original)
                            <>
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
                                      "{flashcards[currentFlashcardIndex].mitzvah.sourceVerse}"
                                    </p>
                                    <p className="text-sm text-blue-700 mt-2">
                                      {flashcards[currentFlashcardIndex].mitzvah.book} {flashcards[currentFlashcardIndex].mitzvah.chapter}:{flashcards[currentFlashcardIndex].mitzvah.verse}
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
                            </>
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
              {!isAuthenticated ? (
                // Guest User - Show sign up prompt
                <Card className="text-center py-12">
                  <CardHeader>
                    <CardTitle className="text-2xl">📊 Track Your Progress</CardTitle>
                    <p className="text-gray-600 mt-4">
                      Sign up to unlock personalized progress tracking, achievement badges, and spaced repetition learning!
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                        <div className="text-center p-4 bg-blue-50 rounded-lg opacity-50">
                          <div className="text-2xl font-bold text-blue-600">?</div>
                          <div className="text-sm text-gray-600">Learning</div>
                        </div>
                        <div className="text-center p-4 bg-yellow-50 rounded-lg opacity-50">
                          <div className="text-2xl font-bold text-yellow-600">?</div>
                          <div className="text-sm text-gray-600">Reviewing</div>
                        </div>
                        <div className="text-center p-4 bg-green-50 rounded-lg opacity-50">
                          <div className="text-2xl font-bold text-green-600">?</div>
                          <div className="text-sm text-gray-600">Mastered</div>
                        </div>
                        <div className="text-center p-4 bg-purple-50 rounded-lg opacity-50">
                          <div className="text-2xl font-bold text-purple-600">?%</div>
                          <div className="text-sm text-gray-600">Overall</div>
                        </div>
                      </div>
                      <Button 
                        onClick={() => setShowAuthModal(true)}
                        className="h-16 px-8"
                      >
                        <div className="text-center">
                          <div className="font-semibold">Sign Up to Track Progress</div>
                          <div className="text-sm opacity-75">Unlock personalized learning features</div>
                        </div>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ) : userProgress ? (
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
              ) : (
                // Authenticated but no progress data yet
                <Card className="text-center py-12">
                  <CardHeader>
                    <CardTitle className="text-2xl">📊 Loading Your Progress...</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600">
                      We're setting up your personalized learning dashboard. Start taking quizzes or reviewing flashcards to see your progress here!
                    </p>
                  </CardContent>
                </Card>
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