# Helper function which checks if a given element is in array
in_array () {
    local array="$1[@]"
    local seeking=$2
    local in=1
    for element in "${!array}"; do
        if [[ $element == $seeking ]]; then
        in=0
        break
    fi
    done
    return $in
}
