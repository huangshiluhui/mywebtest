import JSEncrypt from 'jsencrypt'

// 密钥对生成 http://web.chacuo.net/netrsakeypair

const publicKey = `MFwwDQYJKoZIhvcNAQEBBQADSwAwSAJBAJA5FO7Uexl7mdo61wJsKaP5TIWVWSlV
y6h4JH0xateKlW2viwDzatykz5orhieE88R05Wczw0ZR1bNIho9sKg8CAwEAAQ==`

const privateKey = `MIIBOgIBAAJBAJA5FO7Uexl7mdo61wJsKaP5TIWVWSlVy6h4JH0xateKlW2viwDz
atykz5orhieE88R05Wczw0ZR1bNIho9sKg8CAwEAAQJADVPHb4YUdaRHPg3Xsyi1
Z/ddG8kGl+9bZjWEwn1JdYjISdJMCj1tiVwPDx4xmp6wyPjNf9hq2yh4w+PBO0b9
wQIhAJfSiZ7JODcFrJbUrBsgsMdibJvTPY7aCQj706MNnU9PAiEA8y+cOJAEOSDf
eav56l99N3OA8JLNg6UYk1BL6xfqyUECIDMOKxeJxWzDbLnARSxOPwSd9bYlQINE
kVtDDHW9w1QDAiBvXziOdvZYK4PtNyOngL/Z6137z1+rkKqmnLmIG1X9gQIhAIAH
w2Kt36E8ZIv/2xnzIyOk/lPvfAhfuHEcPdr6BONe`


// 加密
export function encrypt(txt) {
    const encryptor = new JSEncrypt()
    encryptor.setPublicKey(publicKey) // 设置公钥
    return encryptor.encrypt(txt) // 对数据进行加密
}

// 解密
export function decrypt(txt) {
    const encryptor = new JSEncrypt()
    encryptor.setPrivateKey(privateKey) // 设置私钥
    return encryptor.decrypt(txt) // 对数据进行解密
}
