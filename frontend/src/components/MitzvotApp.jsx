import React, { useState, useMemo } from 'react';
import { Search, Filter, BookOpen, Tag, Info } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { allMitzvot, categories, statusTypes } from '../data/mockMitzvot';

const MitzvotApp = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');
  const [selectedBook, setSelectedBook] = useState('all');
  const [viewMode, setViewMode] = useState('cards');

  // Get unique books for filter
  const books = useMemo(() => {
    const uniqueBooks = [...new Set(allMitzvot.map(m => m.book))].sort();
    return uniqueBooks;
  }, []);

  // Filter mitzvot based on search and filters
  const filteredMitzvot = useMemo(() => {
    return allMitzvot.filter(mitzvah => {
      const matchesSearch = searchTerm === '' || 
        mitzvah.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        mitzvah.traditionalWording.toLowerCase().includes(searchTerm.toLowerCase()) ||
        mitzvah.sourceVerse.toLowerCase().includes(searchTerm.toLowerCase()) ||
        mitzvah.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesCategory = selectedCategory === 'all' || mitzvah.category === selectedCategory;
      const matchesStatus = selectedStatus === 'all' || mitzvah.status === selectedStatus;
      const matchesBook = selectedBook === 'all' || mitzvah.book === selectedBook;

      return matchesSearch && matchesCategory && matchesStatus && matchesBook;
    });
  }, [searchTerm, selectedCategory, selectedStatus, selectedBook]);

  const getStatusColor = (status) => {
    const statusType = statusTypes.find(s => s.value === status);
    return statusType ? statusType.color : 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status) => {
    const statusType = statusTypes.find(s => s.value === status);
    return statusType ? statusType.label : status;
  };

  const getCategoryName = (categoryId) => {
    const category = categories.find(c => c.id === categoryId);
    return category ? category.name : categoryId;
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
              <div className="text-2xl font-bold text-blue-600">{allMitzvot.length}</div>
              <div className="text-sm text-gray-600">Total Mitzvot</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-4">
              <div className="text-2xl font-bold text-green-600">
                {allMitzvot.filter(m => m.status === 'direct').length}
              </div>
              <div className="text-sm text-gray-600">Direct Biblical</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-4">
              <div className="text-2xl font-bold text-purple-600">{categories.length}</div>
              <div className="text-sm text-gray-600">Categories</div>
            </CardContent>
          </Card>
          <Card className="text-center">
            <CardContent className="pt-4">
              <div className="text-2xl font-bold text-orange-600">{filteredMitzvot.length}</div>
              <div className="text-sm text-gray-600">Filtered Results</div>
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
                    <SelectItem key={category.id} value={category.id}>
                      {category.name} ({category.count})
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
                  {books.map(book => (
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
            {filteredMitzvot.length} Mitzvot Found
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
              {filteredMitzvot.map(mitzvah => (
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
                      {filteredMitzvot.map(mitzvah => (
                        <MitzvahTableRow key={mitzvah.id} mitzvah={mitzvah} />
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {filteredMitzvot.length === 0 && (
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
      </div>
    </div>
  );
};

export default MitzvotApp;