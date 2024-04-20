#include "fast_cgi.h"

using namespace std;

const char* Names[5] = {"SCRIPT_NAME", "SCRIPT_FILENAME", "QUERY_STRING", "DOCUMENT_ROOT", "REQUEST_METHOD"};
const char* Values[5] = { nullptr, nullptr, "VAR1", "/usr/local/sbin", "GET"};


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
    for(int i=0; i < 5; i++)
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

}

extern "C" const char* fastCgiRequest(int sd, const char* file)
{
    Values[0] = file;
    Values[1] = file;
    FCGI_BeginRequestRecord init_req;
    init_req= {  FCGI_VERSION_1, FCGI_BEGIN_REQUEST, 
        (char)(0x1234 >> 8), ((char)0x1234 & 0xFF),
        0x00, 0x08,  0, 0,
        (char)(FCGI_RESPONDER >> 8), (char)(FCGI_RESPONDER & 0xFF),
        0, 0, 0, 0, 0, 0, 
    };

    sendValidation( write(sd, &init_req, sizeof(FCGI_BeginRequestRecord)) );


    FCGI_Header target_req;
    target_req= {
        FCGI_VERSION_1, FCGI_STDIN, 
        (char)(0x1244 >> 8),(char) (0x1244 & 0xFF),
        0, 0,0, 0,
    };
    sendNameValuePairs(sd);
    sendValidation( write(sd, &target_req, sizeof(FCGI_Header) ) ); 

    char buff[600];
    int size_read = read(sd, buff, 600);

    if(size_read == 0)
    {
        cout << "request error, no response \n";
        exit(-1);
    }
    char* ptr = (char*)malloc( size_read - sizeof(FCGI_Header) + 1);
    memcpy(ptr, buff + sizeof(FCGI_Header),  size_read - sizeof(FCGI_Header));
    ptr[size_read - sizeof(FCGI_Header)] = '\0';

    return ptr;


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
    else
    {
        printf("Socket successfully created..\n");
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
    else
    {
        printf("connected to the server..\n");
    }

    const char* msg = fastCgiRequest(sockfd, "/home/mateusz/python_projects/HttpServer/tests/php1/index.php");

    printf("%s", msg);
    free((void*)msg);
    close(sockfd);
}

#endif