function index_temp = sample_sparse(parent_lat,...
                               parent_long,...
                               parpar_lat,...
                               parpar_long,...
                               LATITUDE,...
                               LONGITUDE,...
                               depth,...
                               total_rem,...
                               index_total,...
                               threshold_down,...
                               threshold_up,...
                               th_phi)

if total_rem ~= length(index_total)
    error('Shit!');
end

cands = [];
for i = 1 : total_rem
    x = [parent_long - LONGITUDE(index_total(i)), parent_lat - LATITUDE(index_total(i))];
    y = -[parpar_long - parent_long, parpar_lat - parent_lat];
    cosphi = (x * y.') / (norm(x) * norm(y));
    distance = norm([LONGITUDE(index_total(i)) - parent_long,...
                                    LATITUDE(index_total(i)) - parent_lat]);
    if distance >= threshold_down && distance <= threshold_up && cosphi <= th_phi
        cands = [cands index_total(i)]; %#ok<AGROW>
    end
end

if length(cands) >= depth
    index = randperm(length(cands), depth);
    index_temp = cands(index);
else
    error('Not Enough Airports!');
end