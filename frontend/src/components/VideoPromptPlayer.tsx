import { useState } from 'react';
import { Loader, Video, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface VideoResponse {
    id: string;
    status: string;
    video_link: string;
}

const VideoPromptPlayer = () => {
    const [query, setQuery] = useState('');
    const [videoUrl, setVideoUrl] = useState<string | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;

        setIsLoading(true);
        setError(null);

        try {
            const response = await fetch('https://notsora-api.itsmesovit.com/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query, rag: false }),
            });

            if (!response.ok) {
                throw new Error('Failed to generate video');
            }

            const data: VideoResponse = await response.json();
            setVideoUrl(data.video_link);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <Card className="w-full max-w-3xl mx-auto">
            <CardHeader>
                <CardTitle className="flex items-center gap-2 text-2xl">
                    <Video className="w-6 h-6 text-blue-500" />
                    AI Video Generator
                </CardTitle>
                <CardDescription>
                    Enter a prompt to generate an AI-powered video
                </CardDescription>
            </CardHeader>

            <CardContent className="space-y-6">
                <form onSubmit={handleSubmit} className="flex gap-3">
                    <Input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Describe the video you want to generate..."
                        className="flex-1"
                        disabled={isLoading}
                    />
                    <Button
                        type="submit"
                        disabled={isLoading}
                        className="min-w-[120px]"
                    >
                        {isLoading ? (
                            <>
                                <Loader className="w-4 h-4 mr-2 animate-spin" />
                                Creating
                            </>
                        ) : (
                            'Generate'
                        )}
                    </Button>
                </form>

                {error && (
                    <Alert variant="destructive">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {videoUrl && (
                    <div className="relative rounded-lg overflow-hidden bg-gradient-to-br from-gray-50 to-gray-100 shadow-inner">
                        <div className="aspect-video">
                            <video
                                src={videoUrl}
                                controls
                                className="absolute inset-0 w-full h-full"
                                key={videoUrl}
                            >
                                Your browser does not support the video tag.
                            </video>
                        </div>
                    </div>
                )}

                {!videoUrl && !isLoading && (
                    <div className="aspect-video rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center text-gray-400">
                        <div className="text-center">
                            <Video className="w-12 h-12 mx-auto mb-2 opacity-40" />
                            <p>Your generated video will appear here</p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default VideoPromptPlayer;