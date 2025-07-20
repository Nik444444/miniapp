import React from 'react';

const EnvCheck = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    const googleClientId = process.env.REACT_APP_GOOGLE_CLIENT_ID;
    
    return (
        <div style={{padding: '20px', fontFamily: 'Arial, sans-serif'}}>
            <h2>Environment Variables Check</h2>
            <p><strong>REACT_APP_BACKEND_URL:</strong> {backendUrl || 'NOT SET'}</p>
            <p><strong>REACT_APP_GOOGLE_CLIENT_ID:</strong> {googleClientId || 'NOT SET'}</p>
            
            <h3>Test Backend Connection</h3>
            <button onClick={async () => {
                try {
                    const response = await fetch(`${backendUrl}/api/auth/telegram/verify`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            user: {
                                id: 123456789,
                                first_name: 'Test'
                            }
                        })
                    });
                    
                    const data = await response.json();
                    console.log('Backend response:', data);
                    alert('Backend connection successful! Check console for details.');
                } catch (error) {
                    console.error('Backend connection error:', error);
                    alert(`Backend connection failed: ${error.message}`);
                }
            }}>
                Test Backend Connection
            </button>
        </div>
    );
};

export default EnvCheck;