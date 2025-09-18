import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, BookOpen, Tag, Info, Loader } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { useToast } from '../hooks/use-toast';
import { Toaster } from './ui/toaster';
import apiService from '../services/api';

const MitzvotApp = () => {
  // State management
  const [mitzvot, setMitzvot] = useState([]);
  const [categories, setCategories] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedBook, setSelectedBook] = useState('all');
  const [viewMode, setViewMode] = useState('cards');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({});

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
  }, [searchTerm, selectedCategory, selectedStatus, selectedBook, currentPage]);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      
      // Load stats and categories in parallel
      const [statsResponse, categoriesResponse] = await Promise.all([
        apiService.getStats(),
        apiService.getCategories()
      ]);

      setStats(statsResponse);
      setCategories(categoriesResponse);
      
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
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            The 613 Laws of the Bible
          </h1>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Explore the complete collection of biblical commandments with their sources, 
            scholarly notes, and categorization. Search by content, filter by origin, 
            and discover the rich tradition of biblical law.
          </p>
        </div>

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
                  {categories.map(category => (
                    <SelectItem key={category.slug} value={category.slug}>
                      {category.name} ({category.count || 0})
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
                  {statusTypes.map(status => (
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
                  {(filters.books || []).map(book => (
                    <SelectItem key={book} value={book}>{book}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* View Mode Toggle */}
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-900">
            {loading ? (
              <span className="flex items-center">
                <Loader className="w-5 h-5 animate-spin mr-2" />
                Loading...
              </span>
            ) : (
              `${mitzvot.length} of ${stats.totalMitzvot || 613} Mitzvot`
            )}
          </h2>
          <Tabs value={viewMode} onValueChange={setViewMode}>
            <TabsList>
              <TabsTrigger value="cards">Card View</TabsTrigger>
              <TabsTrigger value="table">Table View</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>

        {/* Content */}
        <Tabs value={viewMode}>
          <TabsContent value="cards">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {mitzvot.map(mitzvah => (
                <MitzvahCard key={mitzvah.id} mitzvah={mitzvah} />
              ))}
            </div>
          </TabsContent>
          
          <TabsContent value="table">
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="py-3 px-4 text-left font-medium text-gray-900">#</th>
                        <th className="py-3 px-4 text-left font-medium text-gray-900">Law</th>
                        <th className="py-3 px-4 text-left font-medium text-gray-900">Reference</th>
                        <th className="py-3 px-4 text-left font-medium text-gray-900">Origin</th>
                        <th className="py-3 px-4 text-left font-medium text-gray-900">Category</th>
                      </tr>
                    </thead>
                    <tbody>
                      {mitzvot.map(mitzvah => (
                        <MitzvahTableRow key={mitzvah.id} mitzvah={mitzvah} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* No Results */}
        {!loading && mitzvot.length === 0 && (
          <Card className="text-center py-12">
            <CardContent>
              <div className="text-gray-500">
                <Filter className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <h3 className="text-lg font-medium mb-2">No mitzvot found</h3>
                <p>Try adjusting your search terms or filters.</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Pagination */}
        <Pagination />
      </div>
      
      <Toaster />
    </div>
  );
};

export default MitzvotApp;