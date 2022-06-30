# unique-cidr-manager
## _A basic tool build to manage unique CIDR across networks_

[![Network](https://www.baeldung.com/wp-content/uploads/sites/4/2021/02/IPV4vsIPV6-1024x718-1.png)]()

This tool is built in order to manage the private range ip addresses in the organization network to avoid future potential routing conflicts. 

## How it Works

- An env file should be provided in order the set all the required parameters using '--env-file .env'  while running docker
Required parameter name and values:

| name | description | value |
| ------ | ------ | ------ |
| access_token | your personal token for the repo that will contain the unique list of occupied CIDRs |  ghp_3KR4U7bxxxxxxxxxxxxx
| requiredrange | the required major range from list | 10 (or 172 or 192) |


- The tool will first clone a dedicated repo (your own repo) that will maintain the final and unique list of occupide ip ranges. 
- After getting the required major range, it will start choosing first subnet (cidr) in this range, for example 10.0.0.0/26
- Than it will read the already occupied ranges from 'occupied-range.json' file (which should be created in your repo, {} content should be enough) and check if that occupied, if its overlaping it will go to next available range.
- After getting the UNIQUE cidr, it will return the the CIDR to web browser.
- Last step, it will append the new CIDR to the occupied-range.json and will push the change to your repo 


## Docker

unique-cidr-manager is very easy to install and deploy in a Docker container.


```sh
docker build -t image:tag .
```

```sh
docker run -d -p 8000:8000 --env-file env -name unique-cidr-manager unique-cidr-manager:latest
```


Verify the deployment by navigating to your server address in
your preferred browser.

```sh
localhost:8000/get-cidr
```

## License

MIT

**Free Software, Hell Yeah!**
