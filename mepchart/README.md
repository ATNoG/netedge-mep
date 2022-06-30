### Create chart
```bash
#In the current directory
helm package .
```
### Usage
```bash
NS=<namespace>
RELEASE=<release>
# Replace the following parameters to properly connect to OSM mongodb
# Can both be replaced in the values.yaml or via cli
#  mongodb_addr
#  mongodb_port
#  mongodb_database
#  mongodb_password
#  mongodb_username

# Without replace
helm install -n $NS --wait --timeout 15m $RELEASE <chart_name> --debug
# With replace
helm install -n $NS --wait --timeout 15m $RELEASE --mongodb_addr=<...> --set mep.args.mongodb_port=<...> mep.args.mongodb_database=<...> mep.args.mongodb_password=<...> mep.args.mongodb_username=<...> <chart_name> --debug
```
