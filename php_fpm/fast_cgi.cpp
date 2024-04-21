#include "fast_cgi.h"
#include <vector>

using namespace std;

//const char* Names[7] = {"SCRIPT_NAME", "SCRIPT_FILENAME", "QUERY_STRING", "REQUEST_METHOD", "CONTENT_LENGTH", "CONTENT_TYPE", "PHPSESSID"};
//const char* Values[7] = { nullptr, nullptr, "VAR1", nullptr, nullptr, nullptr, nullptr};
int nv_to_send = 0; 
char* buff = nullptr;

vector<const char* > Names;
vector<const char* > Values;
void encodeLen(char* arr, unsigned int size)
{
    unsigned int nameLenByteSize = size <= 127 ? 1 : 4;
    if( nameLenByteSize == 1)
    {
        *arr ^= *arr;
        *arr = (char)size;
        return; 
    }
}

void sendValidation(int i)
{
    if( i == -1 ) 
    {
        printf("send error: %s\n", strerror(errno));
        exit(-1);
    }
}

void sendNameValuePairs(int sd)
{
    char encodedNameLen[4];
    char encodedValueLen[4];
    for(int i=0; i < Names.size(); i++)
    {
        unsigned int nameLength = strlen(Names[i]);
        unsigned int valueLength = strlen(Values[i]);

        unsigned int nameLenByteSize = nameLength <= 127 ? 1 : 4;
        encodeLen(encodedNameLen, nameLength);
        unsigned int valueLenByteSize = valueLength <= 127 ? 1 : 4;
        encodeLen(encodedValueLen, valueLength);

        unsigned short pairSize = nameLength +  valueLength +  nameLenByteSize + valueLenByteSize ;
        char* buffer = (char*) malloc(pairSize + sizeof(FCGI_Header));
        char* ptr_buff = buffer;
        FCGI_Header target_req;
        target_req= {
            FCGI_VERSION_1, FCGI_PARAMS, 
            (char)(0x1244 >> 8),(char) (0x1244 & 0xFF),
            (unsigned char)(pairSize >> 8), (unsigned char)(pairSize & 0xFF),
            0, 0,
        };

        memcpy(ptr_buff, &target_req, sizeof(FCGI_Header));
        ptr_buff += sizeof(FCGI_Header);
        memcpy(ptr_buff, encodedNameLen, nameLenByteSize);
        ptr_buff += nameLenByteSize;
        memcpy(ptr_buff, encodedValueLen, valueLenByteSize);
        ptr_buff += valueLenByteSize;
        memcpy(ptr_buff, Names[i], strlen(Names[i] ));
        ptr_buff += strlen(Names[i]);
        memcpy(ptr_buff, Values[i], strlen(Values[i] ));

        sendValidation( write(sd, buffer, pairSize + sizeof(FCGI_Header)) );
        free(buffer);
    }

    FCGI_Header empty_params;
    empty_params= {
        FCGI_VERSION_1, FCGI_PARAMS, 
        (char)(0x1244 >> 8),(char) (0x1244 & 0xFF),
        0, 0,0, 0,
    };
    sendValidation( write(sd, &empty_params, sizeof(FCGI_Header) ) ); 

}

void beginCgiRequest(int sd)
{
    FCGI_BeginRequestRecord init_req;
    init_req= {  FCGI_VERSION_1, FCGI_BEGIN_REQUEST, 
        (char)(0x1234 >> 8), ((char)0x1234 & 0xFF),
        0x00, 0x08,  0, 0,
        (char)(FCGI_RESPONDER >> 8), (char)(FCGI_RESPONDER & 0xFF),
        0, 0, 0, 0, 0, 0, 
    };

    sendValidation( write(sd, &init_req, sizeof(FCGI_BeginRequestRecord) ) ); 
}

void sendArgsToStdin(int sd, const char* args)
{
    unsigned int len = strlen(args);
    FCGI_Header target_req;
    target_req= {
        FCGI_VERSION_1, FCGI_STDIN , 
        (char)(0x1244 >> 8),(char) (0x1244 & 0xFF),
        (unsigned char)(len >> 8), (unsigned char)(len & 0xFF)
        ,0, 0,
    };
    
    char* stdinBuff = new char[sizeof(FCGI_Header) + len];
    memcpy(stdinBuff, &target_req, sizeof(FCGI_Header));
    memcpy(stdinBuff + sizeof(FCGI_Header), args, len);
    sendValidation( write(sd, stdinBuff, sizeof(FCGI_Header) + len ) ); 
}

void endCgiRequest(int sd)
{
    
    FCGI_Header empty_stdin;
    empty_stdin= {
        FCGI_VERSION_1, FCGI_STDIN, 
        (char)(0x1244 >> 8),(char) (0x1244 & 0xFF),
        0, 0,0, 0,
    };
    sendValidation( write(sd, &empty_stdin, sizeof(FCGI_Header) ) ); 
}
extern "C" const char* fastCgiRequest(int sd, const char* file, const char* method, 
                const char* content = nullptr, const char* content_len = nullptr, 
                        const char* content_type= nullptr, const char* session_id = nullptr)
{
    Names.push_back("SCRIPT_NAME");
    Names.push_back("SCRIPT_FILENAME");
    Names.push_back( "REQUEST_METHOD");
    Names.push_back("QUERY_STRING");

    Values.push_back(file);
    Values.push_back(file);
    Values.push_back(method);
    Values.push_back("VAR1" );

    if( session_id != nullptr)
    {
        Names.push_back("HTTP_COOKIE");
        Values.push_back(session_id);
    }

    if(content != nullptr)
    {   
        Names.push_back("CONTENT_LENGTH");
        Names.push_back("CONTENT_TYPE");
        Values.push_back(content_len);
        Values.push_back(content_type);

        if( content_type == nullptr || content_len == nullptr)
        {
            printf("call requires content_len and content_type to be passed\n");
            exit(-1);
        }

    }

#ifdef VERBOSE
    for(int i =0 ; i < Names.size(); i++)
    {
        printf("Name: %s | Value: %s \n", Names[i], Values[i] );
    }
    if ( content != nullptr)
    {
        printf("content: %s\n", content);
    }
    printf("------------ \n");
#endif
    beginCgiRequest(sd);
    sendNameValuePairs(sd);
    if(content != nullptr)
    {
        sendArgsToStdin(sd, content);
    }
    endCgiRequest(sd);


    if (buff != nullptr)
    {
        printf("buffer memory leak, call  freeBuffer() before processing another request");
        exit(-1);
    }

    char* buff = new char[1200 + 1];
    int size_read = read(sd, buff, 1200);

    if(size_read <= 0)
    {
        printf("read error: %s\n", strerror(errno));;
        exit(-1);
    }
    FCGI_Header* responseHeader =(FCGI_Header*) buff;
    unsigned short stringSize = (responseHeader->contentLengthB1 << 8) | responseHeader->contentLengthB0;

    buff[sizeof(FCGI_Header) + stringSize] = '\0';
    return buff + sizeof(FCGI_Header);
}


extern "C" void freeBuffer()
{
    delete[] buff;
    buff = nullptr;

    Names.clear();
    Values.clear();
}

#ifdef TEST
int main()
{

    int sockfd, connfd;
    struct sockaddr_in servaddr, cli;
 
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) 
    {
        printf("socket creation failed...\n");
        exit(0);
    }

    bzero(&servaddr, sizeof(servaddr));
 
    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");
    servaddr.sin_port = htons(PORT);
 
    // connect the client socket to server socket
    if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr))!= 0) 
    {
        printf("connection with the server failed...\n");
        exit(0);
    }

    //const char* msg = fastCgiRequest(sockfd, "/home/mateusz/python_projects/HttpServer/tests/php2/zaloguj.php", 
        //"POST", "login=25&haslo=1234" ,"19", "application/x-www-form-urlencoded");
    const char* msg = fastCgiRequest(sockfd, "/home/mateusz/python_projects/HttpServer/tests/php2/index.php", 
        "POST", nullptr ,nullptr, nullptr, "PHPSESSID=i6g2fbgvmb6kr90kbn64oi74ik; path=/");
    printf("%s\n", msg);
    freeBuffer();
    close(sockfd);
}

#endif

