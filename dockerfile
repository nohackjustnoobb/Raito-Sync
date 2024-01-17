FROM golang:1-alpine as builder

WORKDIR /app

COPY . .
RUN go mod download

RUN apk update && apk add gcc libc-dev
RUN GOAMD64=v3 CGO_ENABLED=1 go build .

FROM alpine:3 as final
WORKDIR /app

COPY --from=builder /app/Raito-Sync /app/Raito-Sync
RUN chmod +x Raito-Sync

RUN apk add dumb-init
ENTRYPOINT ["/usr/bin/dumb-init", "--"]

EXPOSE 3000
CMD [ "sh", "-c", "/app/Raito-Sync" ]
